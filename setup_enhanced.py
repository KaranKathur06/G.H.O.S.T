"""
G.H.O.S.T. Enhanced Setup Script

This script helps users set up G.H.O.S.T. Enhanced with proper dependencies,
configuration, and initial testing.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def print_banner():
    """Print setup banner."""
    print("=" * 70)
    print("G.H.O.S.T. Enhanced - Autonomous AI Assistant Setup")
    print("=" * 70)
    print()

def check_python_version():
    """Check if Python version is compatible."""
    print("Checking Python version...")
    
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("ERROR: Python 3.8+ required. Current version:", 
              f"{version.major}.{version.minor}.{version.micro}")
        return False
    
    print(f"SUCCESS: Python {version.major}.{version.minor}.{version.micro} - Compatible")
    return True

def install_dependencies():
    """Install required dependencies."""
    print("\n📦 Installing dependencies...")
    
    requirements_file = Path(__file__).parent / "requirements_enhanced.txt"
    
    if not requirements_file.exists():
        print("❌ ERROR: requirements_enhanced.txt not found")
        return False
    
    try:
        # Install dependencies
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Dependencies installed successfully")
            return True
        else:
            print("❌ ERROR installing dependencies:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def setup_directories():
    """Create necessary directories."""
    print("\n📁 Setting up directories...")
    
    directories = [
        "logs",
        "temp",
        "data/config",
        "data/cache"
    ]
    
    for directory in directories:
        dir_path = Path(__file__).parent / directory
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"✅ Created: {directory}")

def create_env_file():
    """Create .env file template."""
    print("\n🔧 Creating configuration files...")
    
    env_file = Path(__file__).parent / ".env"
    
    if not env_file.exists():
        env_content = """# G.H.O.S.T. Enhanced Configuration
# OpenAI API Key (optional but recommended for best performance)
OPENAI_API_KEY=your_openai_api_key_here

# Other API Keys (optional)
OPENWEATHER_API_KEY=your_weather_api_key_here
"""
        
        env_file.write_text(env_content)
        print("✅ Created .env configuration file")
        print("   📝 Edit .env to add your API keys for enhanced functionality")
    else:
        print("✅ .env file already exists")

def test_components():
    """Test core components."""
    print("\n🧪 Testing core components...")
    
    try:
        # Test imports
        print("   Testing imports...")
        
        # Add current directory to path
        sys.path.insert(0, str(Path(__file__).parent))
        
        from core.llm_brain import LLMBrain
        from core.action_dispatcher import ActionDispatcher
        from speech.enhanced_tts import EnhancedTTS
        print("   ✅ Core imports successful")
        
        # Test LLM Brain
        print("   Testing LLM Brain...")
        brain = LLMBrain({'use_openai': False, 'use_ollama': False, 'use_local': False})
        print("   ✅ LLM Brain initialized")
        
        # Test Action Dispatcher
        print("   Testing Action Dispatcher...")
        dispatcher = ActionDispatcher({'require_confirmation': False})
        actions = dispatcher.get_available_actions()
        print(f"   ✅ Action Dispatcher initialized ({len(actions)} actions available)")
        
        # Test TTS
        print("   Testing TTS System...")
        tts = EnhancedTTS({})
        status = tts.get_engine_status()
        print(f"   ✅ TTS System initialized (engine: {status['current_engine']})")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Component test failed: {e}")
        return False

def run_quick_test():
    """Run a quick functionality test."""
    print("\n🚀 Running quick functionality test...")
    
    try:
        import asyncio
        sys.path.insert(0, str(Path(__file__).parent))
        
        from core.llm_brain import LLMBrain
        from core.action_dispatcher import ActionDispatcher
        
        async def test_pipeline():
            # Test LLM to Action pipeline
            brain = LLMBrain({'use_openai': False, 'use_ollama': False, 'use_local': False})
            dispatcher = ActionDispatcher({'require_confirmation': False})
            
            # Test time request
            response = await brain.reason("What time is it?")
            print(f"   LLM Response: {response.content}")
            
            if response.requires_action and response.suggested_actions:
                action = response.suggested_actions[0]
                result = await dispatcher.execute_action(action)
                print(f"   Action Result: {result.message}")
                return result.success
            
            return True
        
        success = asyncio.run(test_pipeline())
        
        if success:
            print("   ✅ Quick test passed - G.H.O.S.T. Enhanced is ready!")
            return True
        else:
            print("   ❌ Quick test failed")
            return False
            
    except Exception as e:
        print(f"   ❌ Quick test error: {e}")
        return False

def print_next_steps():
    """Print next steps for the user."""
    print("\n🎯 SETUP COMPLETE! Next Steps:")
    print()
    print("1. 📝 Edit .env file to add your OpenAI API key (optional but recommended)")
    print("2. 🧪 Run test mode first:")
    print("   python ghost_enhanced.py --test")
    print()
    print("3. 🚀 Start G.H.O.S.T. Enhanced:")
    print("   python ghost_enhanced.py")
    print()
    print("4. 🎤 Say 'Ghost' followed by your command")
    print("   Examples:")
    print("   - 'Ghost, what time is it?'")
    print("   - 'Ghost, open calculator'")
    print("   - 'Ghost, search for Python tutorials'")
    print()
    print("5. 📖 Read README_ENHANCED.md for detailed documentation")
    print()
    print("🤖 G.H.O.S.T. Enhanced is ready to serve you, Sir!")

def main():
    """Main setup function."""
    print_banner()
    
    # Check Python version
    if not check_python_version():
        return 1
    
    # Install dependencies
    if not install_dependencies():
        print("\n❌ Setup failed during dependency installation")
        return 1
    
    # Setup directories
    setup_directories()
    
    # Create configuration files
    create_env_file()
    
    # Test components
    if not test_components():
        print("\n⚠️  Setup completed with warnings - some components may not work properly")
        print("   Check the error messages above and ensure all dependencies are installed")
    
    # Run quick test
    if not run_quick_test():
        print("\n⚠️  Quick test failed - G.H.O.S.T. may not function properly")
        print("   Check your configuration and dependencies")
    
    # Print next steps
    print_next_steps()
    
    return 0

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n🛑 Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed with error: {e}")
        sys.exit(1)
