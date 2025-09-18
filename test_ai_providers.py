#!/usr/bin/env python3
"""
AI Provider Compatibility Testing Script for MCP-Ghidra5
Tests multiple AI providers for compatibility with the MCP server

Copyright (c) 2024 TechSquad Inc. - All Rights Reserved
Proprietary Software - NOT FOR RESALE  
Coded by: TheStingR
"""

import asyncio
import logging
import os
import sys
import json
import time
from typing import Dict, List, Optional, Any
import aiohttp

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIProviderTester:
    """Test multiple AI providers for MCP compatibility"""
    
    def __init__(self):
        self.providers = {
            'openai_gpt4o': {
                'name': 'OpenAI GPT-4o',
                'url': 'https://api.openai.com/v1/chat/completions',
                'model': 'gpt-4o',
                'key_env': 'OPENAI_API_KEY',
                'headers_func': self.openai_headers,
                'cost_per_1k_input': 0.005,
                'cost_per_1k_output': 0.015
            },
            'openai_gpt4': {
                'name': 'OpenAI GPT-4',
                'url': 'https://api.openai.com/v1/chat/completions',
                'model': 'gpt-4',
                'key_env': 'OPENAI_API_KEY', 
                'headers_func': self.openai_headers,
                'cost_per_1k_input': 0.03,
                'cost_per_1k_output': 0.06
            },
            'anthropic_claude': {
                'name': 'Anthropic Claude-3.5-Sonnet',
                'url': 'https://api.anthropic.com/v1/messages',
                'model': 'claude-3-5-sonnet-20241022',
                'key_env': 'ANTHROPIC_API_KEY',
                'headers_func': self.anthropic_headers,
                'cost_per_1k_input': 0.003,
                'cost_per_1k_output': 0.015
            },
            'azure_openai': {
                'name': 'Azure OpenAI',
                'url': None,  # Set via AZURE_OPENAI_ENDPOINT
                'model': 'gpt-4o',
                'key_env': 'AZURE_OPENAI_KEY',
                'headers_func': self.azure_headers,
                'cost_per_1k_input': 0.005,
                'cost_per_1k_output': 0.015
            }
        }
        
        self.test_query = "What is reverse engineering and why is it important in cybersecurity?"
        
    def openai_headers(self, api_key: str) -> Dict[str, str]:
        """OpenAI API headers"""
        return {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
    
    def anthropic_headers(self, api_key: str) -> Dict[str, str]:
        """Anthropic API headers"""
        return {
            'x-api-key': api_key,
            'anthropic-version': '2023-06-01',
            'Content-Type': 'application/json'
        }
    
    def azure_headers(self, api_key: str) -> Dict[str, str]:
        """Azure OpenAI API headers"""
        return {
            'api-key': api_key,
            'Content-Type': 'application/json'
        }
    
    def create_openai_payload(self, model: str, query: str) -> Dict[str, Any]:
        """Create OpenAI API payload"""
        return {
            'model': model,
            'messages': [
                {
                    'role': 'system',
                    'content': 'You are an expert cybersecurity professional specializing in reverse engineering and binary analysis.'
                },
                {
                    'role': 'user', 
                    'content': query
                }
            ],
            'max_tokens': 500,
            'temperature': 0.7
        }
    
    def create_anthropic_payload(self, model: str, query: str) -> Dict[str, Any]:
        """Create Anthropic API payload"""
        return {
            'model': model,
            'max_tokens': 500,
            'messages': [
                {
                    'role': 'user',
                    'content': f'You are an expert cybersecurity professional specializing in reverse engineering and binary analysis. {query}'
                }
            ]
        }
    
    async def test_provider(self, provider_id: str, provider_config: Dict[str, Any]) -> Dict[str, Any]:
        """Test a single AI provider"""
        result = {
            'provider': provider_id,
            'name': provider_config['name'],
            'status': 'unknown',
            'response_time': 0,
            'error': None,
            'response_preview': None,
            'cost_estimate': 0
        }
        
        try:
            # Check if API key is available
            api_key = os.environ.get(provider_config['key_env'])
            if not api_key:
                result['status'] = 'no_api_key'
                result['error'] = f"Environment variable {provider_config['key_env']} not set"
                return result
            
            # Special handling for Azure OpenAI
            url = provider_config['url']
            if provider_id == 'azure_openai':
                endpoint = os.environ.get('AZURE_OPENAI_ENDPOINT')
                if not endpoint:
                    result['status'] = 'no_endpoint'
                    result['error'] = "AZURE_OPENAI_ENDPOINT environment variable not set"
                    return result
                deployment = os.environ.get('AZURE_OPENAI_DEPLOYMENT', 'gpt-4o')
                url = f"{endpoint}/openai/deployments/{deployment}/chat/completions?api-version=2024-02-15-preview"
            
            # Prepare request
            headers = provider_config['headers_func'](api_key)
            
            if provider_id == 'anthropic_claude':
                payload = self.create_anthropic_payload(provider_config['model'], self.test_query)
            else:
                payload = self.create_openai_payload(provider_config['model'], self.test_query)
            
            # Make request
            start_time = time.time()
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload, timeout=30) as response:
                    end_time = time.time()
                    result['response_time'] = round(end_time - start_time, 2)
                    
                    if response.status == 200:
                        data = await response.json()
                        
                        # Extract response text based on provider
                        if provider_id == 'anthropic_claude':
                            response_text = data.get('content', [{}])[0].get('text', '')
                        else:
                            response_text = data.get('choices', [{}])[0].get('message', {}).get('content', '')
                        
                        if response_text:
                            result['status'] = 'success'
                            result['response_preview'] = response_text[:200] + "..." if len(response_text) > 200 else response_text
                            
                            # Estimate cost (rough calculation)
                            input_tokens = len(self.test_query) // 4  # Rough token estimate
                            output_tokens = len(response_text) // 4
                            
                            cost = (input_tokens / 1000 * provider_config['cost_per_1k_input'] + 
                                   output_tokens / 1000 * provider_config['cost_per_1k_output'])
                            result['cost_estimate'] = round(cost, 4)
                        else:
                            result['status'] = 'empty_response'
                            result['error'] = "Received empty response"
                    else:
                        result['status'] = 'api_error'
                        error_data = await response.text()
                        result['error'] = f"HTTP {response.status}: {error_data[:200]}"
                        
        except asyncio.TimeoutError:
            result['status'] = 'timeout'
            result['error'] = "Request timed out after 30 seconds"
        except Exception as e:
            result['status'] = 'exception'
            result['error'] = str(e)
        
        return result
    
    async def test_all_providers(self) -> List[Dict[str, Any]]:
        """Test all configured AI providers"""
        logger.info("🧪 Testing AI Provider Compatibility for MCP-Ghidra5...")
        logger.info("=" * 60)
        
        tasks = []
        for provider_id, config in self.providers.items():
            tasks.append(self.test_provider(provider_id, config))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions
        final_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                provider_id = list(self.providers.keys())[i]
                final_results.append({
                    'provider': provider_id,
                    'name': self.providers[provider_id]['name'],
                    'status': 'exception',
                    'error': str(result),
                    'response_time': 0,
                    'response_preview': None,
                    'cost_estimate': 0
                })
            else:
                final_results.append(result)
        
        return final_results
    
    def print_results(self, results: List[Dict[str, Any]]):
        """Print test results in a formatted way"""
        print("\n🎯 AI Provider Compatibility Test Results")
        print("=" * 60)
        
        working_providers = []
        failed_providers = []
        
        for result in results:
            status_emoji = {
                'success': '✅',
                'no_api_key': '🔑',
                'no_endpoint': '🔗',
                'api_error': '❌',
                'timeout': '⏱️',
                'exception': '💥',
                'empty_response': '📭'
            }.get(result['status'], '❓')
            
            print(f"\n{status_emoji} {result['name']}")
            print(f"   Status: {result['status'].upper()}")
            
            if result['status'] == 'success':
                print(f"   Response Time: {result['response_time']}s")
                print(f"   Cost Estimate: ${result['cost_estimate']}")
                print(f"   Preview: {result['response_preview'][:100]}...")
                working_providers.append(result)
            else:
                print(f"   Error: {result['error']}")
                failed_providers.append(result)
        
        print("\n" + "=" * 60)
        print(f"📊 Summary: {len(working_providers)} working, {len(failed_providers)} failed")
        
        if working_providers:
            print(f"\n✅ Working Providers:")
            for provider in working_providers:
                print(f"   - {provider['name']} ({provider['response_time']}s, ${provider['cost_estimate']})")
        
        if failed_providers:
            print(f"\n❌ Failed Providers:")
            for provider in failed_providers:
                print(f"   - {provider['name']}: {provider['status']}")
        
        print(f"\n💡 To use alternative providers, update the MCP server configuration.")
        
    def generate_config_recommendations(self, results: List[Dict[str, Any]]) -> str:
        """Generate configuration recommendations based on test results"""
        working = [r for r in results if r['status'] == 'success']
        
        if not working:
            return "❌ No AI providers are currently working. Please configure API keys."
        
        # Sort by cost-effectiveness (response time / cost)
        working.sort(key=lambda x: x['response_time'] / max(x['cost_estimate'], 0.001))
        
        recommendations = []
        recommendations.append("🔧 AI Provider Configuration Recommendations:")
        recommendations.append("=" * 50)
        
        best = working[0]
        recommendations.append(f"🥇 Best Overall: {best['name']}")
        recommendations.append(f"   - Response Time: {best['response_time']}s")
        recommendations.append(f"   - Cost: ${best['cost_estimate']} per query")
        
        if len(working) > 1:
            cheapest = min(working, key=lambda x: x['cost_estimate'])
            fastest = min(working, key=lambda x: x['response_time'])
            
            recommendations.append(f"\n💰 Most Cost-Effective: {cheapest['name']} (${cheapest['cost_estimate']})")
            recommendations.append(f"⚡ Fastest Response: {fastest['name']} ({fastest['response_time']}s)")
        
        recommendations.append(f"\n📝 To use {best['name']} as default, update ghidra_gpt5_mcp.py:")
        recommendations.append(f"   GPT_MODEL = \"{best.get('model', 'gpt-4o')}\"")
        
        return "\n".join(recommendations)

async def main():
    """Main testing function"""
    print("🎯 MCP-Ghidra5 AI Provider Compatibility Tester")
    print("Copyright (c) 2024 TechSquad Inc. - All Rights Reserved")
    print("")
    
    tester = AIProviderTester()
    
    # Run tests
    results = await tester.test_all_providers()
    
    # Print results
    tester.print_results(results)
    
    # Generate recommendations
    print("\n" + tester.generate_config_recommendations(results))
    
    # Save results to file
    with open('ai_provider_test_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Detailed results saved to: ai_provider_test_results.json")
    
    return results

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n❌ Testing cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)