#!/usr/bin/env python3
"""
Test chatbot API endpoints
"""

import requests
import json
import time
import subprocess
import sys
import os

def test_api_endpoints():
    """Test backend API endpoints"""

    base_url = "http://localhost:8000"

    print("Testing backend API endpoints...")

    # Test 1: Root endpoint
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        print(f"GET /: Status {response.status_code}")
        if response.status_code == 200:
            print(f"  Response: {response.json()}")
        else:
            print(f"  Error: {response.text}")
    except requests.exceptions.ConnectionError:
        print("GET /: Connection error - server may not be running")
        return False
    except Exception as e:
        print(f"GET /: Error: {str(e)}")
        return False

    # Test 2: Health endpoint
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        print(f"GET /health: Status {response.status_code}")
        if response.status_code == 200:
            print(f"  Response: {response.json()}")
        else:
            print(f"  Error: {response.text}")
    except Exception as e:
        print(f"GET /health: Error: {str(e)}")
        return False

    # Test 3: System info endpoint
    try:
        response = requests.get(f"{base_url}/system-info", timeout=5)
        print(f"GET /system-info: Status {response.status_code}")
        if response.status_code == 200:
            print(f"  Response: {response.json()}")
        else:
            print(f"  Error: {response.text}")
    except Exception as e:
        print(f"GET /system-info: Error: {str(e)}")

    # Test 4: Chat endpoint (POST)
    try:
        chat_data = {
            "question": "What is ROS?",
            "selected_text": None,
            "conversation_id": None
        }
        response = requests.post(
            f"{base_url}/chat",
            json=chat_data,
            timeout=10
        )
        print(f"POST /chat: Status {response.status_code}")
        if response.status_code == 200:
            print(f"  Response: {response.json()}")
        else:
            print(f"  Error: {response.text}")
    except Exception as e:
        print(f"POST /chat: Error: {str(e)}")

    return True

def start_backend_server():
    """Start backend server"""
    print("Starting backend server...")

    # Change to backend directory
    backend_dir = os.path.join(os.path.dirname(__file__), "backend")

    # Activate virtual environment and start server
    venv_activate = os.path.join(os.path.dirname(__file__), "venv", "Scripts", "activate")

    cmd = f'cd "{backend_dir}" && "{sys.executable}" -c "import uvicorn; uvicorn.run(\"main:app\", host=\"127.0.0.1\", port=8000, log_level=\"info\")"'

    # Start server in background
    process = subprocess.Popen(
        cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    print(f"Server started with PID: {process.pid}")
    print("Waiting for server to start...")
    time.sleep(3)  # Give server time to start

    return process

def main():
    """Main function"""
    print("=" * 60)
    print("Chatbot API Testing")
    print("=" * 60)

    # Try to test endpoints first (server might already be running)
    if not test_api_endpoints():
        print("\nServer not running or not responding. Trying to start it...")

        # Start server
        process = start_backend_server()

        # Wait a bit more
        time.sleep(2)

        # Test endpoints again
        if test_api_endpoints():
            print("\n✅ API testing completed successfully!")
        else:
            print("\n❌ API testing failed.")

        # Kill server
        process.terminate()
        process.wait()
        print("Server stopped.")
    else:
        print("\n✅ API testing completed successfully!")

    print("\n" + "=" * 60)
    print("Testing complete")

if __name__ == "__main__":
    main()