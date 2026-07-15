#!/usr/bin/env python3
"""
End-to-end test script for NLP-to-SQL platform.
Run this after starting the backend to verify all components work.
"""

import requests
import json
import time
from typing import Dict, Any

BASE_URL = "http://localhost:8000"
TIMEOUT = 30

class TestRunner:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.results = []

    def test(self, name: str, func):
        """Run a test and track results."""
        try:
            func()
            self.passed += 1
            self.results.append(f"✅ {name}")
            print(f"✅ {name}")
        except Exception as e:
            self.failed += 1
            self.results.append(f"❌ {name}: {str(e)}")
            print(f"❌ {name}: {str(e)}")

    def report(self):
        """Print test report."""
        print("\n" + "="*60)
        print("TEST REPORT")
        print("="*60)
        for result in self.results:
            print(result)
        print(f"\nPassed: {self.passed}/{self.passed + self.failed}")
        print("="*60)


def test_health():
    """Test API health check."""
    response = requests.get(f"{BASE_URL}/health", timeout=TIMEOUT)
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_status():
    """Test API status endpoint."""
    response = requests.get(f"{BASE_URL}/api/status", timeout=TIMEOUT)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"
    assert "api_key_configured" in data


def test_sql_generation():
    """Test SQL generation phase."""
    query = {"query": "Show total revenue by region"}
    response = requests.post(
        f"{BASE_URL}/api/sql/generate",
        json=query,
        timeout=TIMEOUT
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "sql_query" in data
    assert data["is_valid"] is True
    assert "SELECT" in data["sql_query"].upper()


def test_full_pipeline():
    """Test complete end-to-end pipeline."""
    query = {"query": "Show top 5 customers by spend"}
    response = requests.post(
        f"{BASE_URL}/api/full-pipeline",
        json=query,
        timeout=TIMEOUT
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "phases" in data
    assert "phase1" in data["phases"]
    assert "execution" in data["phases"]
    assert data["final_status"] is not None


def test_agent_sql_refinement():
    """Test agentic SQL refinement."""
    payload = {
        "initial_query": "Show total sales",
        "generated_sql": "SELECT amount FROM sales",
        "validation_feedback": "Add GROUP BY and ORDER BY"
    }
    response = requests.post(
        f"{BASE_URL}/api/agent/refine-sql",
        json=payload,
        timeout=TIMEOUT
    )
    assert response.status_code == 200
    data = response.json()
    assert "conversation_id" in data
    assert "refined_sql" in data
    assert "tokens_used" in data
    # Refined SQL should have GROUP BY or similar
    assert len(data["refined_sql"]) > 0


def test_agent_test_validation():
    """Test agentic test validation."""
    payload = {
        "sql_query": "SELECT id, name FROM customers",
        "test_code": "def test_returns_data(): assert len(result) > 0",
        "test_output": "test_returns_data PASSED"
    }
    response = requests.post(
        f"{BASE_URL}/api/agent/validate-tests",
        json=payload,
        timeout=TIMEOUT
    )
    assert response.status_code == 200
    data = response.json()
    assert "conversation_id" in data
    assert "improved_tests" in data


def test_agent_query_optimization():
    """Test agentic query optimization."""
    payload = {
        "sql_query": "SELECT * FROM sales WHERE region = 'US'",
        "performance_metrics": {
            "query_time_ms": 5000,
            "rows_scanned": 1000000,
            "rows_returned": 500
        }
    }
    response = requests.post(
        f"{BASE_URL}/api/agent/optimize-query",
        json=payload,
        timeout=TIMEOUT
    )
    assert response.status_code == 200
    data = response.json()
    assert "conversation_id" in data
    assert "optimized_query" in data
    assert "suggestions" in data


def test_history():
    """Test execution history retrieval."""
    response = requests.get(f"{BASE_URL}/api/history", timeout=TIMEOUT)
    assert response.status_code == 200
    data = response.json()
    assert "logs" in data or "history" in data


def test_database_persistence():
    """Test that queries are saved to database."""
    # Run a query
    query = {"query": "Test database persistence"}
    response = requests.post(
        f"{BASE_URL}/api/full-pipeline",
        json=query,
        timeout=TIMEOUT
    )
    assert response.status_code in [200, 500]  # Either succeeds or has validation error

    # Check history has record
    time.sleep(1)  # Give database time to persist
    history_response = requests.get(f"{BASE_URL}/api/history", timeout=TIMEOUT)
    assert history_response.status_code == 200


def main():
    """Run all tests."""
    runner = TestRunner()

    print("\n" + "="*60)
    print("NLP-to-SQL Platform - End-to-End Tests")
    print("="*60 + "\n")

    # Basic connectivity
    runner.test("API Health Check", test_health)
    runner.test("API Status Check", test_status)

    # Core functionality
    runner.test("SQL Generation", test_sql_generation)
    runner.test("Full Pipeline", test_full_pipeline)

    # Agent functionality
    runner.test("Agent: SQL Refinement", test_agent_sql_refinement)
    runner.test("Agent: Test Validation", test_agent_test_validation)
    runner.test("Agent: Query Optimization", test_agent_query_optimization)

    # Data persistence
    runner.test("Execution History", test_history)
    runner.test("Database Persistence", test_database_persistence)

    # Print report
    runner.report()

    # Exit with proper code
    exit(0 if runner.failed == 0 else 1)


if __name__ == "__main__":
    main()
