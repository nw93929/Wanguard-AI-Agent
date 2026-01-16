"""
API Test Script
===============

Tests the FastAPI endpoints to ensure n8n integration works correctly.

Usage:
    # Start the API server first
    python api.py

    # In another terminal, run tests
    python test_api.py
"""

import requests
import json
import time
import sys

# Fix for Windows console encoding issues
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

API_BASE = "http://localhost:8000"

def test_health_check():
    """Test basic connectivity"""
    print("="*60)
    print("TEST 1: Health Check")
    print("="*60)

    response = requests.get(f"{API_BASE}/health")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    assert response.status_code == 200
    print("✅ Health check passed\n")

def test_single_stock_research():
    """Test single stock analysis endpoint"""
    print("="*60)
    print("TEST 2: Single Stock Research")
    print("="*60)

    payload = {
        "ticker": "AAPL",
        "instructions": "Quick analysis of Apple's competitive position"
    }

    response = requests.post(f"{API_BASE}/research", json=payload)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "queued"
    assert data["ticker"] == "AAPL"
    print("✅ Single stock research queued\n")

    return data["task_id"]

def test_stock_screening():
    """Test batch screening endpoint"""
    print("="*60)
    print("TEST 3: Stock Screening")
    print("="*60)

    payload = {
        "mode": "screening",
        "criteria": "Warren Buffett value investing",
        "max_stocks": 5,
        "sectors": ["Technology", "Healthcare"]
    }

    response = requests.post(f"{API_BASE}/research/screen", json=payload)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "queued"
    print("✅ Stock screening queued\n")

    return data["task_id"]

def test_invalid_request():
    """Test error handling for invalid requests"""
    print("="*60)
    print("TEST 4: Invalid Request Handling")
    print("="*60)

    # Missing required field
    payload = {
        "instructions": "No ticker provided"
    }

    response = requests.post(f"{API_BASE}/research", json=payload)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")

    assert response.status_code == 422  # Validation error
    print("✅ Invalid request properly rejected\n")

def run_all_tests():
    """Run complete test suite"""
    print("\n" + "="*60)
    print(" API INTEGRATION TEST SUITE")
    print("="*60 + "\n")

    try:
        # Test 1: Health check
        test_health_check()

        # Test 2: Single stock
        task_id_single = test_single_stock_research()

        # Test 3: Screening
        task_id_screen = test_stock_screening()

        # Test 4: Error handling
        test_invalid_request()

        print("="*60)
        print("✅ ALL TESTS PASSED!")
        print("="*60)
        print(f"\nTask IDs for tracking:")
        print(f"  Single stock: {task_id_single}")
        print(f"  Screening: {task_id_screen}")
        print(f"\nNote: Tasks are running in background.")
        print(f"Check logs for completion status.")

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
    except requests.exceptions.ConnectionError:
        print(f"\n❌ ERROR: Cannot connect to {API_BASE}")
        print("Make sure the API server is running: python api.py")
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")

if __name__ == "__main__":
    run_all_tests()
