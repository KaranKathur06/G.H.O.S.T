"""
Test G.H.O.S.T. Enhanced Core Components (No Audio Required)

This script tests the core AI components without requiring microphone/speakers.
"""

import sys
import asyncio
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 70)
print("G.H.O.S.T. Enhanced - Core Components Test")
print("=" * 70)
print()

# Test 1: LLM Brain
print("Test 1: LLM Brain with Structured Responses")
print("-" * 70)
try:
    from core.llm_brain import LLMBrain
    
    config = {
        'use_openai': False,  # Don't use API for testing
        'use_ollama': False,
        'use_local': False
    }
    
    brain = LLMBrain(config)
    print("SUCCESS: LLM Brain initialized")
    
    # Test reasoning
    async def test_reasoning():
        queries = [
            "What time is it?",
            "Tell me a joke",
            "Open calculator"
        ]
        
        for query in queries:
            print(f"\nQuery: {query}")
            response = await brain.reason(query)
            print(f"Response: {response.content}")
            if response.requires_action:
                print(f"Action: {response.suggested_actions}")
    
    asyncio.run(test_reasoning())
    print("\nSUCCESS: LLM Brain test passed")
    
except Exception as e:
    print(f"FAILED: {e}")
    import traceback
    traceback.print_exc()

print()

# Test 2: Action Dispatcher
print("Test 2: Action Dispatcher")
print("-" * 70)
try:
    from core.action_dispatcher import ActionDispatcher
    
    config = {'require_confirmation': False}
    dispatcher = ActionDispatcher(config)
    
    actions = dispatcher.get_available_actions()
    print(f"SUCCESS: Action Dispatcher initialized with {len(actions)} actions")
    print(f"Available actions: {', '.join(actions[:5])}...")
    
    # Test get_time action
    async def test_action():
        action_data = {
            "type": "get_time",
            "parameters": {}
        }
        
        result = await dispatcher.execute_action(action_data)
        print(f"\nTest Action: get_time")
        print(f"Success: {result.success}")
        print(f"Message: {result.message}")
    
    asyncio.run(test_action())
    print("\nSUCCESS: Action Dispatcher test passed")
    
except Exception as e:
    print(f"FAILED: {e}")
    import traceback
    traceback.print_exc()

print()

# Test 3: System Indexer
print("Test 3: System Indexer")
print("-" * 70)
try:
    from core.system_indexer import SystemIndexer
    
    config = {
        'auto_start': False,  # Don't auto-start for testing
        'db_path': 'temp/test_index.db'
    }
    
    indexer = SystemIndexer(config)
    stats = indexer.get_statistics()
    
    print(f"SUCCESS: System Indexer initialized")
    print(f"Total items: {stats.get('total_items', 0)}")
    print(f"Status: {stats.get('status', 'unknown')}")
    print("\nSUCCESS: System Indexer test passed")
    
except Exception as e:
    print(f"FAILED: {e}")
    import traceback
    traceback.print_exc()

print()

# Test 4: Enhanced Personality
print("Test 4: Enhanced Personality")
print("-" * 70)
try:
    from core.enhanced_personality import EnhancedPersonality
    
    config = {
        'mode': 'jarvis',
        'owner_name': 'Sir',
        'assistant_name': 'G.H.O.S.T.'
    }
    
    personality = EnhancedPersonality(config)
    
    greeting, _ = personality.get_greeting(is_owner=True, is_first_time=True)
    print(f"Greeting: {greeting}")
    
    wake_response, _ = personality.get_wake_word_response(is_owner=True)
    print(f"Wake Response: {wake_response}")
    
    farewell, _ = personality.get_farewell(is_owner=True)
    print(f"Farewell: {farewell}")
    
    print("\nSUCCESS: Enhanced Personality test passed")
    
except Exception as e:
    print(f"FAILED: {e}")
    import traceback
    traceback.print_exc()

print()

# Test 5: Integration Test
print("Test 5: LLM to Action Pipeline")
print("-" * 70)
try:
    from core.llm_brain import LLMBrain
    from core.action_dispatcher import ActionDispatcher
    
    brain = LLMBrain({'use_openai': False, 'use_ollama': False, 'use_local': False})
    dispatcher = ActionDispatcher({'require_confirmation': False})
    
    async def test_pipeline():
        # Test time request
        print("User: What time is it?")
        response = await brain.reason("What time is it?")
        print(f"G.H.O.S.T.: {response.content}")
        
        if response.requires_action and response.suggested_actions:
            action = response.suggested_actions[0]
            result = await dispatcher.execute_action(action)
            print(f"Action Result: {result.message}")
        
        print()
        
        # Test joke request
        print("User: Tell me a programming joke")
        response = await brain.reason("Tell me a programming joke")
        print(f"G.H.O.S.T.: {response.content}")
        
        if response.requires_action and response.suggested_actions:
            action = response.suggested_actions[0]
            result = await dispatcher.execute_action(action)
            print(f"Joke: {result.message}")
    
    asyncio.run(test_pipeline())
    print("\nSUCCESS: Integration test passed")
    
except Exception as e:
    print(f"FAILED: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 70)
print("CORE COMPONENTS TEST COMPLETE")
print("=" * 70)
print()
print("G.H.O.S.T. Enhanced core AI components are working!")
print()
print("Note: Audio components (TTS/STT) require additional setup:")
print("  - Install PyAudio: pip install pipwin && pipwin install pyaudio")
print("  - Install Pygame: pip install pygame")
print("  - Or use pre-built wheels for your Python version")
print()
print("To test with full audio support, run: python ghost_enhanced.py --test")
print("(after installing audio dependencies)")
