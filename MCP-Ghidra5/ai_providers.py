#!/usr/bin/env python3
"""
Multi-Model AI Provider Support for Ghidra GPT-5 MCP Server
Supports OpenAI, Claude, Gemini, Grok, DeepSeek, local LLMs, and more

Copyright (c) 2024 TechSquad Inc. - All Rights Reserved  
Proprietary Software - NOT FOR RESALE
Coded by: TheStingR
"""

import asyncio
import aiohttp
import json
import logging
import os
import subprocess
import time
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
from dataclasses import dataclass

logger = logging.getLogger(__name__)

class AIProvider(Enum):
    """Available AI providers"""
    OPENAI = "openai"
    CLAUDE = "claude" 
    GEMINI = "gemini"
    GROK = "grok"
    PERPLEXITY = "perplexity"
    DEEPSEEK = "deepseek"
    OLLAMA = "ollama"
    LOCAL_API = "local_api"

@dataclass
class ModelConfig:
    """Configuration for AI models"""
    provider: AIProvider
    model_name: str
    api_endpoint: str
    max_tokens: int
    cost_per_1k_input: float
    cost_per_1k_output: float
    supports_system_prompt: bool = True
    requires_auth: bool = True
    timeout: int = 120

# Model configurations
MODEL_CONFIGS = {
    # OpenAI Models
    "gpt-4o": ModelConfig(
        provider=AIProvider.OPENAI,
        model_name="gpt-4o",
        api_endpoint="https://api.openai.com/v1/chat/completions",
        max_tokens=4000,
        cost_per_1k_input=0.005,
        cost_per_1k_output=0.015
    ),
    "gpt-4": ModelConfig(
        provider=AIProvider.OPENAI,
        model_name="gpt-4",
        api_endpoint="https://api.openai.com/v1/chat/completions",
        max_tokens=4000,
        cost_per_1k_input=0.03,
        cost_per_1k_output=0.06
    ),
    
    # Claude Models (Anthropic)
    "claude-3-5-sonnet": ModelConfig(
        provider=AIProvider.CLAUDE,
        model_name="claude-3-5-sonnet-20241022",
        api_endpoint="https://api.anthropic.com/v1/messages",
        max_tokens=4000,
        cost_per_1k_input=0.003,
        cost_per_1k_output=0.015
    ),
    "claude-3-opus": ModelConfig(
        provider=AIProvider.CLAUDE,
        model_name="claude-3-opus-20240229",
        api_endpoint="https://api.anthropic.com/v1/messages",
        max_tokens=4000,
        cost_per_1k_input=0.015,
        cost_per_1k_output=0.075
    ),
    
    # Gemini Models (Google)
    "gemini-pro": ModelConfig(
        provider=AIProvider.GEMINI,
        model_name="gemini-pro",
        api_endpoint="https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent",
        max_tokens=4000,
        cost_per_1k_input=0.00025,
        cost_per_1k_output=0.0005
    ),
    "gemini-1.5-pro": ModelConfig(
        provider=AIProvider.GEMINI,
        model_name="gemini-1.5-pro",
        api_endpoint="https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent",
        max_tokens=4000,
        cost_per_1k_input=0.00125,
        cost_per_1k_output=0.005
    ),
    
    # Grok Models (xAI)
    "grok-beta": ModelConfig(
        provider=AIProvider.GROK,
        model_name="grok-beta",
        api_endpoint="https://api.x.ai/v1/chat/completions",
        max_tokens=4000,
        cost_per_1k_input=0.005,
        cost_per_1k_output=0.015
    ),
    
    # Perplexity Models
    "pplx-70b-online": ModelConfig(
        provider=AIProvider.PERPLEXITY,
        model_name="llama-3.1-70b-instruct",
        api_endpoint="https://api.perplexity.ai/chat/completions",
        max_tokens=4000,
        cost_per_1k_input=0.001,
        cost_per_1k_output=0.001
    ),
    
    # DeepSeek Models
    "deepseek-chat": ModelConfig(
        provider=AIProvider.DEEPSEEK,
        model_name="deepseek-chat",
        api_endpoint="https://api.deepseek.com/chat/completions",
        max_tokens=4000,
        cost_per_1k_input=0.00014,
        cost_per_1k_output=0.00028
    ),
    
    # Local Models via Ollama
    "llama3.2": ModelConfig(
        provider=AIProvider.OLLAMA,
        model_name="llama3.2:latest",
        api_endpoint="http://localhost:11434/api/chat",
        max_tokens=4000,
        cost_per_1k_input=0.0,
        cost_per_1k_output=0.0,
        requires_auth=False
    ),
    "code-llama": ModelConfig(
        provider=AIProvider.OLLAMA,
        model_name="codellama:latest",
        api_endpoint="http://localhost:11434/api/chat",
        max_tokens=4000,
        cost_per_1k_input=0.0,
        cost_per_1k_output=0.0,
        requires_auth=False
    ),
    "qwen2.5": ModelConfig(
        provider=AIProvider.OLLAMA,
        model_name="qwen2.5:latest",
        api_endpoint="http://localhost:11434/api/chat",
        max_tokens=4000,
        cost_per_1k_input=0.0,
        cost_per_1k_output=0.0,
        requires_auth=False
    )
}

class AIModelManager:
    """Manages multiple AI providers and model selection"""
    
    def __init__(self):
        self.default_model = os.environ.get('DEFAULT_AI_MODEL', 'gpt-4o')
        self.fallback_models = [
            'claude-3-5-sonnet',
            'gemini-1.5-pro', 
            'grok-beta',
            'llama3.2',
            'pplx-70b-online'
        ]
        self.usage_stats = {}
        
    def get_api_key(self, provider: AIProvider) -> Optional[str]:
        """Get API key for specific provider"""
        key_mapping = {
            AIProvider.OPENAI: ['OPENAI_API_KEY', 'CHATGPT_COOKIE'],
            AIProvider.CLAUDE: ['ANTHROPIC_API_KEY', 'CLAUDE_API_KEY'],
            AIProvider.GEMINI: ['GEMINI_API_KEY', 'GOOGLE_API_KEY'],
            AIProvider.GROK: ['GROK_API_KEY', 'XAI_API_KEY'],
            AIProvider.PERPLEXITY: ['PERPLEXITY_API_KEY', 'PPLX_API_KEY'],
            AIProvider.DEEPSEEK: ['DEEPSEEK_API_KEY'],
            AIProvider.OLLAMA: [],  # No API key needed
            AIProvider.LOCAL_API: ['LOCAL_API_KEY']
        }
        
        for key_name in key_mapping.get(provider, []):
            key = os.environ.get(key_name)
            if key and key.strip():
                return key.strip()
        
        return None
    
    def is_model_available(self, model_name: str) -> bool:
        """Check if a model is available and configured"""
        if model_name not in MODEL_CONFIGS:
            return False
            
        config = MODEL_CONFIGS[model_name]
        
        # Check for local models
        if config.provider == AIProvider.OLLAMA:
            return self._check_ollama_model(model_name)
        
        # Check for API key
        if config.requires_auth and not self.get_api_key(config.provider):
            return False
            
        return True
    
    def _check_ollama_model(self, model_name: str) -> bool:
        """Check if Ollama model is available locally"""
        try:
            result = subprocess.run(
                ['curl', '-s', 'http://localhost:11434/api/tags'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                models_data = json.loads(result.stdout)
                installed_models = [m['name'] for m in models_data.get('models', [])]
                config = MODEL_CONFIGS[model_name]
                return config.model_name in installed_models
        except:
            pass
        return False
    
    def get_best_available_model(self, preferred_model: Optional[str] = None) -> str:
        """Get the best available model, with fallback options"""
        # Try preferred model first
        if preferred_model and self.is_model_available(preferred_model):
            return preferred_model
        
        # Try default model
        if self.is_model_available(self.default_model):
            return self.default_model
        
        # Try fallback models
        for model in self.fallback_models:
            if self.is_model_available(model):
                logger.info(f"Using fallback model: {model}")
                return model
        
        # If nothing else works, return the default and let it fail gracefully
        logger.warning("No AI models available, using default")
        return self.default_model
    
    async def query_model(self, 
                         messages: List[Dict[str, str]], 
                         model_name: Optional[str] = None,
                         max_tokens: Optional[int] = None) -> Tuple[str, Dict[str, Any]]:
        """Query specified model with automatic fallback"""
        
        # Select best available model
        selected_model = self.get_best_available_model(model_name)
        config = MODEL_CONFIGS[selected_model]
        
        # Track usage
        self._track_usage(selected_model)
        
        try:
            # Route to appropriate provider
            if config.provider == AIProvider.OPENAI:
                response = await self._query_openai(messages, config, max_tokens)
            elif config.provider == AIProvider.CLAUDE:
                response = await self._query_claude(messages, config, max_tokens)
            elif config.provider == AIProvider.GEMINI:
                response = await self._query_gemini(messages, config, max_tokens)
            elif config.provider == AIProvider.GROK:
                response = await self._query_grok(messages, config, max_tokens)
            elif config.provider == AIProvider.PERPLEXITY:
                response = await self._query_perplexity(messages, config, max_tokens)
            elif config.provider == AIProvider.DEEPSEEK:
                response = await self._query_deepseek(messages, config, max_tokens)
            elif config.provider == AIProvider.OLLAMA:
                response = await self._query_ollama(messages, config, max_tokens)
            else:
                raise Exception(f"Unsupported provider: {config.provider}")
            
            # Calculate cost
            tokens_used = len(response) // 4  # Rough estimation
            cost = self._calculate_cost(tokens_used, config)
            
            metadata = {
                "model": selected_model,
                "provider": config.provider.value,
                "tokens_used": tokens_used,
                "estimated_cost": cost
            }
            
            logger.info(f"AI query successful: {selected_model} (${cost:.4f})")
            return response, metadata
            
        except Exception as e:
            logger.error(f"Model {selected_model} failed: {e}")
            
            # Try fallback if this wasn't already a fallback
            if selected_model != self.default_model and model_name == selected_model:
                logger.info("Trying fallback model...")
                return await self.query_model(messages, None, max_tokens)
            
            raise Exception(f"All AI models failed. Last error: {str(e)}")
    
    async def _query_openai(self, messages: List[Dict], config: ModelConfig, max_tokens: Optional[int]) -> str:
        """Query OpenAI models"""
        api_key = self.get_api_key(AIProvider.OPENAI)
        if not api_key:
            raise Exception("OpenAI API key not found")
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": config.model_name,
            "messages": messages,
            "max_tokens": max_tokens or config.max_tokens,
            "temperature": 0.1
        }
        
        timeout = aiohttp.ClientTimeout(total=config.timeout)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(config.api_endpoint, headers=headers, json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    return result['choices'][0]['message']['content']
                else:
                    error_text = await response.text()
                    raise Exception(f"OpenAI API error {response.status}: {error_text}")
    
    async def _query_claude(self, messages: List[Dict], config: ModelConfig, max_tokens: Optional[int]) -> str:
        """Query Claude models"""
        api_key = self.get_api_key(AIProvider.CLAUDE)
        if not api_key:
            raise Exception("Anthropic API key not found")
        
        headers = {
            "x-api-key": api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        
        # Convert OpenAI format to Claude format
        system_message = ""
        claude_messages = []
        
        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            else:
                claude_messages.append(msg)
        
        payload = {
            "model": config.model_name,
            "max_tokens": max_tokens or config.max_tokens,
            "messages": claude_messages,
            "temperature": 0.1
        }
        
        if system_message:
            payload["system"] = system_message
        
        timeout = aiohttp.ClientTimeout(total=config.timeout)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(config.api_endpoint, headers=headers, json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    return result['content'][0]['text']
                else:
                    error_text = await response.text()
                    raise Exception(f"Claude API error {response.status}: {error_text}")
    
    async def _query_gemini(self, messages: List[Dict], config: ModelConfig, max_tokens: Optional[int]) -> str:
        """Query Gemini models"""
        api_key = self.get_api_key(AIProvider.GEMINI)
        if not api_key:
            raise Exception("Gemini API key not found")
        
        # Convert messages to Gemini format
        contents = []
        for msg in messages:
            role = "user" if msg["role"] in ["user", "system"] else "model"
            contents.append({
                "role": role,
                "parts": [{"text": msg["content"]}]
            })
        
        payload = {
            "contents": contents,
            "generationConfig": {
                "maxOutputTokens": max_tokens or config.max_tokens,
                "temperature": 0.1
            }
        }
        
        url = f"{config.api_endpoint}?key={api_key}"
        
        timeout = aiohttp.ClientTimeout(total=config.timeout)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(url, json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    return result['candidates'][0]['content']['parts'][0]['text']
                else:
                    error_text = await response.text()
                    raise Exception(f"Gemini API error {response.status}: {error_text}")
    
    async def _query_grok(self, messages: List[Dict], config: ModelConfig, max_tokens: Optional[int]) -> str:
        """Query Grok models (xAI)"""
        api_key = self.get_api_key(AIProvider.GROK)
        if not api_key:
            raise Exception("Grok API key not found")
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "messages": messages,
            "model": config.model_name,
            "max_tokens": max_tokens or config.max_tokens,
            "temperature": 0.1,
            "stream": False
        }
        
        timeout = aiohttp.ClientTimeout(total=config.timeout)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(config.api_endpoint, headers=headers, json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    return result['choices'][0]['message']['content']
                else:
                    error_text = await response.text()
                    raise Exception(f"Grok API error {response.status}: {error_text}")
    
    async def _query_perplexity(self, messages: List[Dict], config: ModelConfig, max_tokens: Optional[int]) -> str:
        """Query Perplexity models"""
        api_key = self.get_api_key(AIProvider.PERPLEXITY)
        if not api_key:
            raise Exception("Perplexity API key not found")
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": config.model_name,
            "messages": messages,
            "max_tokens": max_tokens or config.max_tokens,
            "temperature": 0.1
        }
        
        timeout = aiohttp.ClientTimeout(total=config.timeout)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(config.api_endpoint, headers=headers, json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    return result['choices'][0]['message']['content']
                else:
                    error_text = await response.text()
                    raise Exception(f"Perplexity API error {response.status}: {error_text}")
    
    async def _query_deepseek(self, messages: List[Dict], config: ModelConfig, max_tokens: Optional[int]) -> str:
        """Query DeepSeek models"""
        api_key = self.get_api_key(AIProvider.DEEPSEEK)
        if not api_key:
            raise Exception("DeepSeek API key not found")
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": config.model_name,
            "messages": messages,
            "max_tokens": max_tokens or config.max_tokens,
            "temperature": 0.1,
            "stream": False
        }
        
        timeout = aiohttp.ClientTimeout(total=config.timeout)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(config.api_endpoint, headers=headers, json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    return result['choices'][0]['message']['content']
                else:
                    error_text = await response.text()
                    raise Exception(f"DeepSeek API error {response.status}: {error_text}")
    
    async def _query_ollama(self, messages: List[Dict], config: ModelConfig, max_tokens: Optional[int]) -> str:
        """Query local Ollama models"""
        # Convert to Ollama format
        payload = {
            "model": config.model_name,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": 0.1,
                "num_predict": max_tokens or config.max_tokens
            }
        }
        
        timeout = aiohttp.ClientTimeout(total=config.timeout)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(config.api_endpoint, json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    return result['message']['content']
                else:
                    error_text = await response.text()
                    raise Exception(f"Ollama API error {response.status}: {error_text}")
    
    def _track_usage(self, model_name: str):
        """Track model usage statistics"""
        if model_name not in self.usage_stats:
            self.usage_stats[model_name] = 0
        self.usage_stats[model_name] += 1
    
    def _calculate_cost(self, tokens: int, config: ModelConfig) -> float:
        """Calculate estimated cost for API call"""
        if config.cost_per_1k_input == 0.0:  # Free/local models
            return 0.0
        
        # Rough estimation: 70% input, 30% output
        input_tokens = int(tokens * 0.7)
        output_tokens = int(tokens * 0.3)
        
        input_cost = (input_tokens / 1000) * config.cost_per_1k_input
        output_cost = (output_tokens / 1000) * config.cost_per_1k_output
        
        return round(input_cost + output_cost, 4)
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics"""
        total_calls = sum(self.usage_stats.values())
        
        available_models = []
        for model_name in MODEL_CONFIGS.keys():
            if self.is_model_available(model_name):
                available_models.append(model_name)
        
        return {
            "default_model": self.default_model,
            "available_models": available_models,
            "total_models": len(MODEL_CONFIGS),
            "total_calls": total_calls,
            "usage_by_model": self.usage_stats,
            "most_used_model": max(self.usage_stats.items(), key=lambda x: x[1])[0] if self.usage_stats else None
        }
    
    def list_providers(self) -> Dict[str, List[str]]:
        """List all providers and their models"""
        providers = {}
        for model_name, config in MODEL_CONFIGS.items():
            provider_name = config.provider.value
            if provider_name not in providers:
                providers[provider_name] = []
            
            status = "✅" if self.is_model_available(model_name) else "❌"
            cost_info = "Free" if config.cost_per_1k_input == 0.0 else f"${config.cost_per_1k_input:.4f}/$k"
            
            providers[provider_name].append(f"{status} {model_name} ({cost_info})")
        
        return providers

# Global model manager instance
model_manager = AIModelManager()

async def query_ai_with_fallback(messages: List[Dict[str, str]], 
                                operation_type: str = "analysis",
                                preferred_model: Optional[str] = None) -> Tuple[str, Dict[str, Any]]:
    """
    Enhanced AI query function with multi-model support and fallback
    
    Args:
        messages: List of message dictionaries
        operation_type: Type of operation (analysis, exploit, query)
        preferred_model: Preferred model name (optional)
    
    Returns:
        Tuple of (response_text, metadata)
    """
    
    # Determine max tokens based on operation type
    max_tokens_map = {
        "analysis": 4000,
        "exploit": 3000, 
        "query": 2000
    }
    max_tokens = max_tokens_map.get(operation_type, 2000)
    
    # Use environment variable for model selection if available
    if not preferred_model:
        preferred_model = os.environ.get('AI_MODEL_PREFERENCE')
    
    try:
        response, metadata = await model_manager.query_model(messages, preferred_model, max_tokens)
        
        # Log successful query
        provider = metadata.get('provider', 'unknown')
        model = metadata.get('model', 'unknown')
        cost = metadata.get('estimated_cost', 0)
        
        logger.info(f"AI query successful: {model} ({provider}) - ${cost:.4f}")
        
        return response, metadata
        
    except Exception as e:
        logger.error(f"AI query failed: {str(e)}")
        raise Exception(f"All AI providers failed: {str(e)}")

def get_model_status() -> Dict[str, Any]:
    """Get comprehensive status of all AI models"""
    return {
        "timestamp": time.time(),
        "model_manager": model_manager.get_usage_stats(),
        "providers": model_manager.list_providers(),
        "environment_keys": {
            provider.value: bool(model_manager.get_api_key(provider)) 
            for provider in AIProvider
        }
    }