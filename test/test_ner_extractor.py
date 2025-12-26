
from rotoreader.service.ner_extractor import extract_injuries_and_status


def test_extract_injuries_and_status_with_data():
    """Test NER extraction with sample injury text."""
    text = "Packers QB Aaron Rodgers is questionable with a toe injury."
    injuries, status = extract_injuries_and_status(text)

    # Verify extraction
    assert status == "questionable"
    assert "toe injury" in injuries or "toe" in injuries or "injury" in injuries


def test_extract_injuries_and_status_empty_text():
    """Test NER extraction with empty text."""
    injuries, status = extract_injuries_and_status("")

    assert injuries == []
    assert status == ""


def test_extract_injuries_and_status_no_entities():
    """Test NER extraction with text containing no injury/status entities."""
    text = "The team had a great practice session today."
    injuries, status = extract_injuries_and_status(text)

    # Should return empty results when no entities found
    assert injuries == []
    assert status == ""
