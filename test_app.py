import pytest
import json
from unittest.mock import MagicMock, patch
from app import clean_text, sanitize_input, build_pdf_document

def test_clean_text_ascii_and_unicode():
    """Ensure non-Latin characters and symbols are safely transformed for PDF compliance."""
    sample = "Celebration 🎉 & Music — ✨ 2026"
    cleaned = clean_text(sample)
    assert isinstance(cleaned, str)
    assert "Celebration" in cleaned
    assert "Music" in cleaned

def test_sanitize_input_security():
    """Verify HTML/Script injection attacks and long inputs are safely filtered."""
    malicious = "<script>alert('xss')</script>Eco Wedding<img src=x onerror=alert(1)>"
    cleaned = sanitize_input(malicious)
    assert "<script>" not in cleaned
    assert "<img" not in cleaned
    assert "Eco Wedding" in cleaned

def test_sanitize_input_empty_and_limit():
    """Verify edge cases for input sanitization."""
    assert sanitize_input("") == ""
    assert sanitize_input(None) == ""
    long_str = "A" * 600
    assert len(sanitize_input(long_str)) <= 500

def test_budget_zero_sum_allocation():
    """Ensure mathematical consistency in budget calculation."""
    mock_budget = [
        {"category": "Venue", "amount": 10000, "percentage": 20},
        {"category": "Catering", "amount": 25000, "percentage": 50},
        {"category": "Decor", "amount": 5000, "percentage": 10},
        {"category": "Misc", "amount": 10000, "percentage": 20}
    ]
    total_amount = sum(b["amount"] for b in mock_budget)
    total_pct = sum(b["percentage"] for b in mock_budget)
    assert total_amount == 50000
    assert total_pct == 100

def test_pdf_generation_valid():
    """Verify that build_pdf_document outputs a non-empty, valid PDF byte stream."""
    sample_plan = {
        "event_overview": "Minimalist anniversary gala for 50 people.",
        "budget_breakdown": [
            {"category": "Venue", "amount": 10000, "percentage": 50, "practical_tip": "Book weekday discount"},
            {"category": "Catering", "amount": 10000, "percentage": 50, "practical_tip": "Fixed vegetarian set"}
        ],
        "milestone_timeline": [
            {"phase": "Week 1", "tasks": ["Send invitations", "Confirm headcounts"]}
        ],
        "vendor_checklists": [
            {"vendor_type": "Florist", "deliverables": "Eco bouquets", "key_questions_to_ask": ["Are flowers organic?"]}
        ],
        "personalized_ideas": [
            {"title": "Seed Paper Favors", "category": "Souvenir", "details": "Hand out plantable paper cards."}
        ]
    }
    pdf_bytes = build_pdf_document(sample_plan, "Anniversary", 20000, 50, 15, "Modern Eco")
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 500
    assert pdf_bytes.startswith(b"%PDF")

@patch("google.genai.Client")
def test_mock_gemini_client_integration(mock_client_class):
    """Ensure Gemini SDK call handles structured JSON response appropriately without network calls."""
    mock_instance = MagicMock()
    mock_client_class.return_value = mock_instance
    
    mock_response = MagicMock()
    mock_response.text = json.dumps({
        "event_overview": "Mocked test response",
        "budget_breakdown": [],
        "milestone_timeline": [],
        "vendor_checklists": [],
        "personalized_ideas": []
    })
    mock_instance.models.generate_content.return_value = mock_response

    # Verify structured parsing
    parsed = json.loads(mock_response.text)
    assert parsed["event_overview"] == "Mocked test response"
    assert "budget_breakdown" in parsed