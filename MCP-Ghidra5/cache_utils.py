#!/usr/bin/env python3
"""
Cache and Performance Optimization Utilities for Ghidra GPT-5 MCP Server
Provides result caching, token optimization, and analysis persistence

Copyright (c) 2024 TechSquad Inc. - All Rights Reserved
Proprietary Software - NOT FOR RESALE
Coded by: TheStingR
"""

import os
import json
import hashlib
import pickle
import sqlite3
import time
import logging
from pathlib import Path
from typing import Any, Dict, Optional, List, Tuple
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Cache configuration
CACHE_DIR = os.environ.get('MCP_CACHE_DIR', '/tmp/ghidra_mcp_cache')
CACHE_DB = os.path.join(CACHE_DIR, 'analysis_cache.db')
MAX_CACHE_SIZE_MB = int(os.environ.get('MAX_CACHE_SIZE_MB', '500'))  # 500MB default
CACHE_EXPIRY_HOURS = int(os.environ.get('CACHE_EXPIRY_HOURS', '24'))  # 24 hours default
ENABLE_CACHE = os.environ.get('ENABLE_MCP_CACHE', 'true').lower() == 'true'

class AnalysisCache:
    """Manages caching of analysis results"""
    
    def __init__(self):
        """Initialize cache system"""
        if not ENABLE_CACHE:
            logger.info("Cache disabled by environment variable")
            return
            
        self.cache_dir = Path(CACHE_DIR)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self._init_database()
        self._cleanup_expired()
        logger.info(f"Cache initialized: {self.cache_dir}")
    
    def _init_database(self):
        """Initialize SQLite database for cache metadata"""
        try:
            with sqlite3.connect(CACHE_DB) as conn:
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS cache_entries (
                        cache_key TEXT PRIMARY KEY,
                        file_hash TEXT NOT NULL,
                        analysis_type TEXT NOT NULL,
                        parameters_hash TEXT NOT NULL,
                        created_at TIMESTAMP NOT NULL,
                        last_accessed TIMESTAMP NOT NULL,
                        result_size_bytes INTEGER NOT NULL,
                        result_file TEXT NOT NULL
                    )
                ''')
                
                conn.execute('''
                    CREATE INDEX IF NOT EXISTS idx_created_at ON cache_entries(created_at)
                ''')
                
                conn.execute('''
                    CREATE INDEX IF NOT EXISTS idx_last_accessed ON cache_entries(last_accessed)
                ''')
                
        except Exception as e:
            logger.error(f"Cache database initialization failed: {e}")
    
    def _cleanup_expired(self):
        """Remove expired cache entries"""
        if not ENABLE_CACHE:
            return
            
        try:
            cutoff_time = datetime.now() - timedelta(hours=CACHE_EXPIRY_HOURS)
            
            with sqlite3.connect(CACHE_DB) as conn:
                # Get expired entries
                cursor = conn.execute('''
                    SELECT cache_key, result_file FROM cache_entries 
                    WHERE created_at < ?
                ''', (cutoff_time,))
                
                expired_entries = cursor.fetchall()
                
                # Remove files and database entries
                for cache_key, result_file in expired_entries:
                    try:
                        result_path = self.cache_dir / result_file
                        if result_path.exists():
                            result_path.unlink()
                        logger.debug(f"Removed expired cache entry: {cache_key}")
                    except Exception as e:
                        logger.warning(f"Failed to remove cache file {result_file}: {e}")
                
                # Remove database entries
                conn.execute('DELETE FROM cache_entries WHERE created_at < ?', (cutoff_time,))
                deleted_count = conn.total_changes
                
                if deleted_count > 0:
                    logger.info(f"Cleaned up {deleted_count} expired cache entries")
                    
        except Exception as e:
            logger.error(f"Cache cleanup failed: {e}")
    
    def _calculate_cache_key(self, binary_path: str, analysis_type: str, parameters: Dict[str, Any]) -> str:
        """Calculate unique cache key for analysis"""
        try:
            # Get file hash for binary
            file_hash = self._calculate_file_hash(binary_path)
            
            # Create parameters hash
            params_str = json.dumps(parameters, sort_keys=True)
            params_hash = hashlib.sha256(params_str.encode()).hexdigest()[:16]
            
            # Combine into cache key
            cache_key = f"{analysis_type}_{file_hash[:16]}_{params_hash}"
            return cache_key
            
        except Exception as e:
            logger.error(f"Cache key calculation failed: {e}")
            return None
    
    def _calculate_file_hash(self, file_path: str, algorithm: str = 'sha256') -> str:
        """Calculate file hash for cache validation"""
        try:
            hash_func = getattr(hashlib, algorithm)()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_func.update(chunk)
            return hash_func.hexdigest()
        except Exception as e:
            logger.error(f"File hash calculation failed: {e}")
            return ""
    
    def get_cached_result(self, binary_path: str, analysis_type: str, parameters: Dict[str, Any]) -> Optional[Any]:
        """Retrieve cached analysis result"""
        if not ENABLE_CACHE:
            return None
            
        try:
            cache_key = self._calculate_cache_key(binary_path, analysis_type, parameters)
            if not cache_key:
                return None
            
            with sqlite3.connect(CACHE_DB) as conn:
                cursor = conn.execute('''
                    SELECT file_hash, result_file, created_at FROM cache_entries 
                    WHERE cache_key = ?
                ''', (cache_key,))
                
                row = cursor.fetchone()
                if not row:
                    logger.debug(f"Cache miss: {cache_key}")
                    return None
                
                cached_file_hash, result_file, created_at = row
                
                # Verify file hasn't changed
                current_file_hash = self._calculate_file_hash(binary_path)
                if current_file_hash != cached_file_hash:
                    logger.debug(f"Cache invalidated (file changed): {cache_key}")
                    self._remove_cache_entry(cache_key)
                    return None
                
                # Load cached result
                result_path = self.cache_dir / result_file
                if not result_path.exists():
                    logger.warning(f"Cache file missing: {result_file}")
                    self._remove_cache_entry(cache_key)
                    return None
                
                with open(result_path, 'rb') as f:
                    result = pickle.load(f)
                
                # Update last accessed time
                conn.execute('''
                    UPDATE cache_entries SET last_accessed = ? WHERE cache_key = ?
                ''', (datetime.now(), cache_key))
                
                logger.info(f"Cache hit: {cache_key} (created: {created_at})")
                return result
                
        except Exception as e:
            logger.error(f"Cache retrieval failed: {e}")
            return None
    
    def cache_result(self, binary_path: str, analysis_type: str, parameters: Dict[str, Any], result: Any) -> bool:
        """Cache analysis result"""
        if not ENABLE_CACHE:
            return False
            
        try:
            cache_key = self._calculate_cache_key(binary_path, analysis_type, parameters)
            if not cache_key:
                return False
            
            # Create unique result filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            result_file = f"{cache_key}_{timestamp}.pkl"
            result_path = self.cache_dir / result_file
            
            # Save result to file
            with open(result_path, 'wb') as f:
                pickle.dump(result, f)
            
            result_size = result_path.stat().st_size
            
            # Check cache size limits
            if not self._check_cache_size_limit(result_size):
                result_path.unlink()
                return False
            
            # Store metadata in database
            file_hash = self._calculate_file_hash(binary_path)
            params_hash = hashlib.sha256(json.dumps(parameters, sort_keys=True).encode()).hexdigest()[:16]
            
            with sqlite3.connect(CACHE_DB) as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO cache_entries 
                    (cache_key, file_hash, analysis_type, parameters_hash, created_at, last_accessed, result_size_bytes, result_file)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (cache_key, file_hash, analysis_type, params_hash, datetime.now(), datetime.now(), result_size, result_file))
            
            logger.info(f"Cached result: {cache_key} ({result_size} bytes)")
            return True
            
        except Exception as e:
            logger.error(f"Cache storage failed: {e}")
            return False
    
    def _check_cache_size_limit(self, new_entry_size: int) -> bool:
        """Check if cache size is within limits"""
        try:
            # Calculate current cache size
            total_size = 0
            for cache_file in self.cache_dir.glob("*.pkl"):
                total_size += cache_file.stat().st_size
            
            max_size_bytes = MAX_CACHE_SIZE_MB * 1024 * 1024
            projected_size = total_size + new_entry_size
            
            if projected_size > max_size_bytes:
                logger.info(f"Cache size limit reached ({total_size/1024/1024:.1f}MB), cleaning up...")
                self._cleanup_lru_entries(new_entry_size)
            
            return True
            
        except Exception as e:
            logger.error(f"Cache size check failed: {e}")
            return False
    
    def _cleanup_lru_entries(self, needed_space: int):
        """Remove least recently used entries to make space"""
        try:
            with sqlite3.connect(CACHE_DB) as conn:
                # Get LRU entries
                cursor = conn.execute('''
                    SELECT cache_key, result_file, result_size_bytes FROM cache_entries 
                    ORDER BY last_accessed ASC
                ''')
                
                freed_space = 0
                entries_to_remove = []
                
                for cache_key, result_file, size_bytes in cursor:
                    entries_to_remove.append((cache_key, result_file))
                    freed_space += size_bytes
                    
                    # Stop when we've freed enough space
                    if freed_space >= needed_space:
                        break
                
                # Remove files and database entries
                for cache_key, result_file in entries_to_remove:
                    try:
                        result_path = self.cache_dir / result_file
                        if result_path.exists():
                            result_path.unlink()
                        conn.execute('DELETE FROM cache_entries WHERE cache_key = ?', (cache_key,))
                        logger.debug(f"Removed LRU cache entry: {cache_key}")
                    except Exception as e:
                        logger.warning(f"Failed to remove LRU cache file {result_file}: {e}")
                
                logger.info(f"Freed {freed_space/1024/1024:.1f}MB of cache space")
                
        except Exception as e:
            logger.error(f"LRU cleanup failed: {e}")
    
    def _remove_cache_entry(self, cache_key: str):
        """Remove specific cache entry"""
        try:
            with sqlite3.connect(CACHE_DB) as conn:
                cursor = conn.execute('SELECT result_file FROM cache_entries WHERE cache_key = ?', (cache_key,))
                row = cursor.fetchone()
                
                if row:
                    result_file = row[0]
                    result_path = self.cache_dir / result_file
                    if result_path.exists():
                        result_path.unlink()
                    
                    conn.execute('DELETE FROM cache_entries WHERE cache_key = ?', (cache_key,))
                    
        except Exception as e:
            logger.error(f"Cache entry removal failed: {e}")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        if not ENABLE_CACHE:
            return {"enabled": False}
            
        try:
            with sqlite3.connect(CACHE_DB) as conn:
                cursor = conn.execute('SELECT COUNT(*), SUM(result_size_bytes) FROM cache_entries')
                count, total_size = cursor.fetchone()
                
                cursor = conn.execute('''
                    SELECT analysis_type, COUNT(*) FROM cache_entries 
                    GROUP BY analysis_type
                ''')
                by_type = dict(cursor.fetchall())
                
                # Get oldest and newest entries
                cursor = conn.execute('SELECT MIN(created_at), MAX(created_at) FROM cache_entries')
                oldest, newest = cursor.fetchone()
                
                return {
                    "enabled": True,
                    "total_entries": count or 0,
                    "total_size_mb": (total_size or 0) / 1024 / 1024,
                    "max_size_mb": MAX_CACHE_SIZE_MB,
                    "expiry_hours": CACHE_EXPIRY_HOURS,
                    "entries_by_type": by_type,
                    "oldest_entry": oldest,
                    "newest_entry": newest,
                    "cache_directory": str(self.cache_dir)
                }
                
        except Exception as e:
            logger.error(f"Cache stats failed: {e}")
            return {"enabled": True, "error": str(e)}
    
    def clear_cache(self) -> bool:
        """Clear all cache entries"""
        if not ENABLE_CACHE:
            return False
            
        try:
            # Remove all cache files
            for cache_file in self.cache_dir.glob("*.pkl"):
                cache_file.unlink()
            
            # Clear database
            with sqlite3.connect(CACHE_DB) as conn:
                conn.execute('DELETE FROM cache_entries')
                cleared_count = conn.total_changes
            
            logger.info(f"Cleared {cleared_count} cache entries")
            return True
            
        except Exception as e:
            logger.error(f"Cache clear failed: {e}")
            return False

class TokenOptimizer:
    """Optimizes API token usage"""
    
    @staticmethod
    def optimize_prompt(prompt: str, max_tokens: int = 4000) -> str:
        """Optimize prompt to fit within token limits"""
        # Rough estimation: 4 characters = 1 token
        estimated_tokens = len(prompt) // 4
        
        if estimated_tokens <= max_tokens:
            return prompt
        
        # Truncate while preserving important sections
        lines = prompt.split('\n')
        important_keywords = [
            'security', 'vulnerability', 'exploit', 'buffer overflow',
            'malware', 'analysis', 'function', 'binary', 'address'
        ]
        
        # Keep lines with important keywords
        important_lines = []
        other_lines = []
        
        for line in lines:
            if any(keyword in line.lower() for keyword in important_keywords):
                important_lines.append(line)
            else:
                other_lines.append(line)
        
        # Start with important lines
        result_lines = important_lines
        current_length = sum(len(line) for line in important_lines)
        
        # Add other lines until we approach the limit
        target_length = max_tokens * 3  # Conservative estimate
        
        for line in other_lines:
            if current_length + len(line) < target_length:
                result_lines.append(line)
                current_length += len(line)
            else:
                break
        
        optimized = '\n'.join(result_lines)
        
        if len(optimized) < len(prompt):
            logger.info(f"Optimized prompt from {len(prompt)} to {len(optimized)} characters")
        
        return optimized
    
    @staticmethod
    def calculate_cost_estimate(tokens_used: int, model: str = "gpt-4o") -> float:
        """Calculate estimated cost for API call"""
        # Pricing as of 2024 (approximate)
        pricing = {
            "gpt-4o": {"input": 0.005, "output": 0.015},  # per 1K tokens
            "gpt-4": {"input": 0.03, "output": 0.06},
            "gpt-3.5-turbo": {"input": 0.0015, "output": 0.002}
        }
        
        model_pricing = pricing.get(model, pricing["gpt-4o"])
        
        # Assume 70% input, 30% output tokens
        input_tokens = int(tokens_used * 0.7)
        output_tokens = int(tokens_used * 0.3)
        
        cost = (input_tokens / 1000 * model_pricing["input"]) + \
               (output_tokens / 1000 * model_pricing["output"])
        
        return round(cost, 4)

# Global cache instance
cache = AnalysisCache()
optimizer = TokenOptimizer()

def cached_analysis(analysis_type: str):
    """Decorator for caching analysis results"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Extract parameters for caching
            if args and isinstance(args[0], dict):
                arguments = args[0]
                binary_path = arguments.get("binary_path")
                
                if binary_path and ENABLE_CACHE:
                    # Try to get cached result
                    cached_result = cache.get_cached_result(binary_path, analysis_type, arguments)
                    if cached_result:
                        logger.info(f"Using cached result for {analysis_type}")
                        return cached_result
            
            # Run analysis
            result = await func(*args, **kwargs)
            
            # Cache the result
            if binary_path and result and ENABLE_CACHE:
                cache.cache_result(binary_path, analysis_type, arguments, result)
            
            return result
        
        return wrapper
    return decorator