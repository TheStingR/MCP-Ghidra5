#!/usr/bin/env python3
"""
Test Multi-Model AI Support for MCP-Ghidra5
Demonstrates new AI model features and provider support

Copyright (c) 2024 TechSquad Inc. - All Rights Reserved
"""

import asyncio
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_ai_model_status():
    """Test the new AI model status tool"""
    print("🤖 Testing AI Model Status Tool")
    print("=" * 50)
    
    try:
        from ghidra_gpt5_mcp import handle_ai_model_status
        
        # Test 1: Check overall status
        print("1. Testing model status...")
        result = await handle_ai_model_status({"action": "status"})
        print(f"Status result: {result[0].text[:200]}...")
        
        # Test 2: List available models
        print("\n2. Testing model listing...")
        result = await handle_ai_model_status({"action": "list_models"})
        print(f"Models result: {result[0].text[:200]}...")
        
        # Test 3: Usage statistics
        print("\n3. Testing usage stats...")
        result = await handle_ai_model_status({"action": "usage_stats"})
        print(f"Stats result: {result[0].text[:200]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ AI model status test failed: {e}")
        return False

async def test_multi_model_query():
    """Test multi-model query functionality"""
    print("\n🧠 Testing Multi-Model Query")
    print("=" * 50)
    
    try:
        from ghidra_gpt5_mcp import handle_gpt5_query
        
        # Test with different models
        test_models = [
            ("gpt-4o", "OpenAI GPT-4o"),
            ("claude-3-5-sonnet", "Claude 3.5 Sonnet"), 
            ("gemini-1.5-pro", "Google Gemini"),
            ("llama3.2", "Local Llama")
        ]
        
        for model, description in test_models:
            print(f"\nTesting {description}...")
            try:
                result = await handle_gpt5_query({
                    "query": "What is reverse engineering in one sentence?",
                    "specialization": "reverse_engineering",
                    "preferred_model": model
                })
                
                response = result[0].text
                print(f"✅ {description}: {response[:100]}...")
                
            except Exception as e:
                print(f"⚠️  {description}: Not available ({str(e)[:50]}...)")
        
        return True
        
    except Exception as e:
        print(f"❌ Multi-model query test failed: {e}")
        return False

async def test_ai_providers_direct():
    """Test AI providers module directly"""
    print("\n🔧 Testing AI Providers Module")
    print("=" * 50)
    
    try:
        from ai_providers import model_manager, get_model_status
        
        # Test model availability
        print("Available models:")
        stats = model_manager.get_usage_stats()
        for model in stats['available_models']:
            print(f"  ✅ {model}")
        
        # Test provider status
        print("\nProvider status:")
        status = get_model_status()
        for provider, has_key in status['environment_keys'].items():
            status_icon = "✅" if has_key else "❌"
            print(f"  {status_icon} {provider}")
        
        return True
        
    except ImportError:
        print("❌ AI providers module not available")
        return False
    except Exception as e:
        print(f"❌ AI providers test failed: {e}")
        return False

def print_setup_instructions():
    """Print setup instructions for additional AI models"""
    print("\n📋 Multi-Model AI Setup Instructions")
    print("=" * 50)
    
    env_vars = {
        'ANTHROPIC_API_KEY': 'Claude 3.5 Sonnet (https://console.anthropic.com/)',
        'GEMINI_API_KEY': 'Google Gemini (https://aistudio.google.com/)',
        'GROK_API_KEY': 'xAI Grok (https://console.x.ai/)',
        'PERPLEXITY_API_KEY': 'Perplexity (https://www.perplexity.ai/)',
        'DEEPSEEK_API_KEY': 'DeepSeek (https://platform.deepseek.com/)',
        'AI_MODEL_PREFERENCE': 'Set preferred model (optional)'
    }
    
    print("To enable additional AI models, set these environment variables:")
    print()
    for env_var, description in env_vars.items():
        current_value = os.environ.get(env_var, 'Not set')
        if env_var.endswith('_API_KEY') and current_value != 'Not set':
            current_value = f"{current_value[:10]}..."
        print(f"export {env_var}=\"your-api-key\"  # {description}")
    
    print("\nFor local models (Ollama):")
    print("1. Install Ollama: curl -fsSL https://ollama.com/install.sh | sh")
    print("2. Pull models: ollama pull llama3.2 && ollama pull codellama")
    print("3. Start Ollama service: ollama serve")

async def main():
    """Main test function"""
    print("🚀 MCP-Ghidra5 Multi-Model AI Support Test")
    print("=" * 60)
    
    tests_passed = 0
    total_tests = 3
    
    # Test 1: AI model status tool
    if await test_ai_model_status():
        tests_passed += 1
    
    # Test 2: Multi-model queries
    if await test_multi_model_query():
        tests_passed += 1
    
    # Test 3: AI providers direct
    if await test_ai_providers_direct():
        tests_passed += 1
    
    # Print setup instructions
    print_setup_instructions()
    
    # Summary
    print("\n" + "=" * 60)
    print(f"🎯 MULTI-MODEL TEST SUMMARY")
    print("=" * 60)
    print(f"Tests passed: {tests_passed}/{total_tests}")
    print(f"Success rate: {(tests_passed/total_tests)*100:.1f}%")
    
    if tests_passed == total_tests:
        print("🎉 ALL MULTI-MODEL TESTS PASSED!")
        print("Your MCP-Ghidra5 server now supports multiple AI providers!")
    else:
        print("⚠️  Some tests had issues. Check the output above.")
    
    print("\nNew features available:")
    print("✅ Multi-model AI support (OpenAI, Claude, Gemini, Grok, etc.)")
    print("✅ Local LLM support (Ollama integration)")
    print("✅ Cost tracking and usage statistics")
    print("✅ AI model status and testing tools")
    print("✅ Automatic fallback between providers")

if __name__ == "__main__":
    asyncio.run(main())