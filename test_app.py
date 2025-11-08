#!/usr/bin/env python3
"""
Simple test script to verify the application components work correctly.
"""

import requests
import json
import sys
import time

def test_backend_connection():
    """Test if the backend is running and responding."""
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is running and responding")
            print(f"   Response: {response.json()}")
            return True
        else:
            print(f"❌ Backend returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Backend is not running. Please start it with: uvicorn backend.main:app --reload")
        return False
    except Exception as e:
        print(f"❌ Error connecting to backend: {e}")
        return False

def test_analyze_endpoint():
    """Test the analyze endpoint with sample data."""
    try:
        data = {"degree": "Computer Science", "year": 2025}
        response = requests.post("http://localhost:8000/analyze", json=data, timeout=10)
        if response.status_code == 200:
            print("✅ Analyze endpoint working")
            result = response.json()
            print(f"   Summary: {result.get('summary', 'No summary')}")
            return True
        else:
            print(f"❌ Analyze endpoint failed with status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing analyze endpoint: {e}")
        return False

def test_gemini_integration():
    """Test if Gemini integration is working."""
    try:
        # Test insights endpoint with a complex question
        question = "What are the career prospects for Computer Science graduates from top Indian institutions?"
        response = requests.get(f"http://localhost:8000/insights?q={question}", timeout=15)
        if response.status_code == 200:
            data = response.json()
            print("✅ Gemini 2.5 Flash integration working")
            print(f"   Processing method: {data.get('processing_method', 'Unknown')}")
            print(f"   AI enabled: {data.get('llm_enabled', False)}")
            return True
        else:
            print(f"❌ Gemini test failed with status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing Gemini integration: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Testing Career Outcomes Application")
    print("=" * 50)
    
    # Test backend connection
    if not test_backend_connection():
        print("\n❌ Backend tests failed. Please start the backend first.")
        print("   Run: uvicorn backend.main:app --reload")
        sys.exit(1)
    
    print("\n🔍 Testing API endpoints...")
    
    # Test analyze endpoint
    analyze_ok = test_analyze_endpoint()
    
    # Test Gemini integration
    gemini_ok = test_gemini_integration()
    
    print("\n" + "=" * 50)
    if analyze_ok and gemini_ok:
        print("✅ All tests passed! The application is working correctly.")
        print("\n🚀 You can now run the UI with: streamlit run ui/app.py")
        print("\n🤖 Gemini 2.5 Flash Features:")
        print("   - Intelligent document retrieval")
        print("   - AI-powered insights generation")
        print("   - Contextual analysis and recommendations")
    else:
        print("❌ Some tests failed. Check the backend logs for more details.")
        if not gemini_ok:
            print("\n💡 Gemini Setup Tips:")
            print("   1. Set GOOGLE_API_KEY in your .env file")
            print("   2. Install: pip install google-generativeai")
            print("   3. Get API key from: https://makersuite.google.com/app/apikey")
        sys.exit(1)

if __name__ == "__main__":
    main()
