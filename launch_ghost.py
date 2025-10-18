#!/usr/bin/env python3
"""
G.H.O.S.T. Enhanced - Simple Launcher

This script provides an easy way to launch G.H.O.S.T. Enhanced with
different modes and automatic setup if needed.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def print_banner():
    """Print G.H.O.S.T. Enhanced banner."""
    print("🤖" + "=" * 60 + "🤖")
    print("🚀 G.H.O.S.T. Enhanced - Autonomous AI Assistant")
    print("🤖" + "=" * 60 + "🤖")
    print()

def check_setup():
    """Check if G.H.O.S.T. Enhanced is properly set up."""
    project_root = Path(__file__).parent
    
    # Check for required files
    required_files = [
        "ghost_enhanced.py",
        "requirements_enhanced.txt",
        "core/llm_brain.py",
        "core/action_dispatcher.py",
        "speech/enhanced_tts.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not (project_root / file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ Missing required files:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        return False
    
    # Check if dependencies are installed
    try:
        import openai
        import edge_tts
        import pygame
        print("✅ Dependencies verified")
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("   Run setup first: python setup_enhanced.py")
        return False
    
    return True

def run_setup():
    """Run the setup script."""
    print("🔧 Running G.H.O.S.T. Enhanced setup...")
    setup_script = Path(__file__).parent / "setup_enhanced.py"
    
    if not setup_script.exists():
        print("❌ Setup script not found!")
        return False
    
    try:
        result = subprocess.run([sys.executable, str(setup_script)], check=True)
        return result.returncode == 0
    except subprocess.CalledProcessError:
        print("❌ Setup failed!")
        return False

def launch_ghost(mode="normal", config_file=None, debug=False):
    """Launch G.H.O.S.T. Enhanced with specified options."""
    project_root = Path(__file__).parent
    ghost_script = project_root / "ghost_enhanced.py"
    
    if not ghost_script.exists():
        print("❌ G.H.O.S.T. Enhanced script not found!")
        return False
    
    # Build command
    cmd = [sys.executable, str(ghost_script)]
    
    if mode == "test":
        cmd.append("--test")
        print("🧪 Launching G.H.O.S.T. Enhanced in TEST mode...")
    elif mode == "debug":
        cmd.append("--debug")
        print("🐛 Launching G.H.O.S.T. Enhanced in DEBUG mode...")
    else:
        print("🚀 Launching G.H.O.S.T. Enhanced in NORMAL mode...")
    
    if config_file:
        cmd.extend(["--config", config_file])
        print(f"📝 Using config file: {config_file}")
    
    if debug and mode != "debug":
        cmd.append("--debug")
    
    print()
    print("🎤 G.H.O.S.T. Enhanced will start listening for 'Ghost' wake word...")
    print("💡 Try commands like:")
    print("   - 'Ghost, what time is it?'")
    print("   - 'Ghost, open calculator'")
    print("   - 'Ghost, search for Python tutorials'")
    print()
    print("Press Ctrl+C to stop G.H.O.S.T.")
    print("-" * 60)
    
    try:
        # Launch G.H.O.S.T. Enhanced
        subprocess.run(cmd, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ G.H.O.S.T. Enhanced failed to start: {e}")
        return False
    except KeyboardInterrupt:
        print("\n🛑 Launch cancelled by user")
        return True

def main():
    """Main launcher function."""
    parser = argparse.ArgumentParser(
        description="G.H.O.S.T. Enhanced Launcher",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python launch_ghost.py                    # Normal mode
  python launch_ghost.py --test             # Test mode
  python launch_ghost.py --debug            # Debug mode
  python launch_ghost.py --setup            # Run setup first
  python launch_ghost.py --config my.json   # Custom config
        """
    )
    
    parser.add_argument(
        "--test", 
        action="store_true", 
        help="Launch in test mode with sample commands"
    )
    
    parser.add_argument(
        "--debug", 
        action="store_true", 
        help="Launch in debug mode with verbose logging"
    )
    
    parser.add_argument(
        "--setup", 
        action="store_true", 
        help="Run setup before launching"
    )
    
    parser.add_argument(
        "--config", 
        type=str, 
        help="Path to custom configuration file"
    )
    
    parser.add_argument(
        "--force-setup", 
        action="store_true", 
        help="Force setup even if system appears ready"
    )
    
    args = parser.parse_args()
    
    print_banner()
    
    # Run setup if requested or needed
    if args.setup or args.force_setup or not check_setup():
        if not run_setup():
            print("❌ Setup failed. Cannot launch G.H.O.S.T. Enhanced.")
            return 1
        print("✅ Setup completed successfully!")
        print()
    
    # Determine launch mode
    if args.test:
        mode = "test"
    elif args.debug:
        mode = "debug"
    else:
        mode = "normal"
    
    # Launch G.H.O.S.T. Enhanced
    success = launch_ghost(
        mode=mode, 
        config_file=args.config, 
        debug=args.debug
    )
    
    if success:
        print("\n✅ G.H.O.S.T. Enhanced session completed")
        return 0
    else:
        print("\n❌ G.H.O.S.T. Enhanced failed to launch")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n🛑 Launcher interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Launcher error: {e}")
        sys.exit(1)
