#!/usr/bin/env python3
"""
Setup script for Multi-Agent AI System
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        print(f"❌ Python 3.8+ required. Current version: {python_version.major}.{python_version.minor}")
        return False
    print(f"✅ Python version {python_version.major}.{python_version.minor}.{python_version.micro} is compatible")
    return True

def install_dependencies():
    """Install Python dependencies"""
    if not os.path.exists("requirements.txt"):
        print("❌ requirements.txt not found")
        return False
    
    return run_command(
        f"{sys.executable} -m pip install -r requirements.txt",
        "Installing Python dependencies"
    )

def setup_environment():
    """Set up environment configuration"""
    env_example = Path(".env.example")
    env_file = Path(".env")
    
    if env_example.exists():
        if not env_file.exists():
            shutil.copy(env_example, env_file)
            print("✅ Created .env file from .env.example")
            print("⚠️  Please edit .env file with your API keys")
        else:
            print("ℹ️  .env file already exists")
    else:
        print("❌ .env.example not found")
        return False
    
    return True

def create_directories():
    """Create necessary directories"""
    directories = ["outputs", "logs", "data"]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Created directory: {directory}")
    
    return True

def run_tests():
    """Run the test suite"""
    if os.path.exists("tests"):
        return run_command(
            f"{sys.executable} -m pytest tests/ -v",
            "Running test suite"
        )
    else:
        print("⚠️  Tests directory not found, skipping tests")
        return True

def main():
    """Main setup process"""
    print("🚀 Multi-Agent AI System Setup")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create directories
    if not create_directories():
        print("❌ Failed to create directories")
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Failed to install dependencies")
        sys.exit(1)
    
    # Setup environment
    if not setup_environment():
        print("❌ Failed to setup environment")
        sys.exit(1)
    
    # Run tests (optional)
    print("\n🧪 Would you like to run the test suite? (y/n): ", end="")
    if input().lower().startswith('y'):
        run_tests()
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Edit .env file with your API keys")
    print("2. Run: python src/main.py")
    print("3. Or try examples: python examples/basic_multi_agent.py")
    print("\n📚 Documentation: README.md")

if __name__ == "__main__":
    main()
