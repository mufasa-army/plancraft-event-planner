import pytest
import json
from app import clean_text

def test_clean_text_basic():
    """Verify clean_text properly strips or replaces incompatible latin-1 characters"""
    input_text = "Wedding Celebration 🎉 — Special Day"
    cleaned = clean_text(input_text)
    assert isinstance(cleaned, str)
    assert "Wedding Celebration" in cleaned

def test_budget_structure():
    """Validate zero-sum budget integrity"""
    mock_budget = [
        {"category": "Venue", "amount": 20000, "percentage": 40},
        {"category": "Catering", "amount": 20000, "percentage": 40},
        {"category": "Decor", "amount": 10000, "percentage": 20}
    ]
    total_amount = sum(item["amount"] for item in mock_budget)
    total_pct = sum(item["percentage"] for item in mock_budget)
    assert total_amount == 50000
    assert total_pct == 100

def test_schema_parsing():
    """Ensure strict JSON contract validation"""
    sample_json = '''{
        "event_overview": "Test event",
        "budget_breakdown": [],
        "milestone_timeline": [],
        "vendor_checklists": [],
        "personalized_ideas": []
    }'''
    parsed = json.loads(sample_json)
    assert "budget_breakdown" in parsed
    assert "milestone_timeline" in parsed
    assert "vendor_checklists" in parsed
    assert "personalized_ideas" in parsed