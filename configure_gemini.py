#!/usr/bin/env python3
"""
Configuration script to set up Google API key for Career Outcomes Agent
"""

import os
import sys
from dotenv import load_dotenv

def create_env_file():
    """Create .env file with the provided API key."""
    api_key = "AIzaSyC0Siwre9uXAvzLK4n-74QG-gGutUoCrWQ"

    env_content = f"""# Career Outcomes Agent - Environment Configuration

# Google Gemini Configuration (Required for AI features)
GOOGLE_API_KEY={api_key}

# Optional: Other LLM providers
OPENAI_API_KEY=your_openai_api_key_here
HUGGINGFACEHUB_API_TOKEN=your_hf_token_here

# Server Configuration
HOST=0.0.0.0
PORT=8000

# Data Configuration
DATA_DIR=backend/data

# Embeddings Model (optional)
EMBEDDINGS_MODEL=models/embedding-001
"""

    try:
        with open(".env", "w") as f:
            f.write(env_content)
        print("✅ .env file created successfully with your Google API key!")
        print(f"   API Key: {api_key[:10]}...{api_key[-10:]}")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False


def test_api_key():
    """Test if the API key works by listing and using a valid model."""
    try:
        import google.generativeai as genai

        # Load key from .env
        load_dotenv()
        api_key = os.getenv("GOOGLE_API_KEY")

        if not api_key:
            print("❌ GOOGLE_API_KEY not found in .env")
            return False

        # Configure Gemini
        genai.configure(api_key=api_key)

        # List available models
        print("🔍 Fetching available Gemini models...")
        models = [m.name for m in genai.list_models()]
        valid_models = [m for m in models if "gemini" in m.lower()]

        if not valid_models:
            print("❌ No Gemini models found for this API key.")
            print("   Make sure the API key is from https://makersuite.google.com/app/apikey")
            return False

        # Pick the first valid model
        model_name = valid_models[0]
        print(f"✅ Found available model: {model_name}")

        # Test generation
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("Hello, this is a test of the Gemini API.")

        print("✅ API key test successful!")
        print(f"   Model: {model_name}")
        print(f"   Response: {response.text[:60]}...")
        return True

    except ImportError:
        print("❌ google-generativeai not installed")
        print("   Run: pip install google-generativeai")
        return False
    except Exception as e:
        print(f"❌ API key test failed:\n   {e}")
        return False


def main():
    """Main configuration function."""
    print("🔧 Career Outcomes Agent - Gemini Configuration Setup")
    print("=" * 60)

    # Skip creating env if it already exists
    if os.path.exists(".env"):
        print(f"✅ Loaded API key from .env ({os.path.abspath('.env')})")
    else:
        if not create_env_file():
            print("❌ Failed to create .env")
            sys.exit(1)

    print("\n🧪 Testing API key...")
    if test_api_key():
        print("\n🎉 Configuration complete! You’re all set to use Gemini API.")
    else:
        print("\n⚠️  API key test failed. Please verify your key or internet connection.")


if __name__ == "__main__":
    main()
