import logging

from transformers import pipeline

logger = logging.getLogger(__name__)

# Model configuration
MODEL_ID = "maxo99/sports-injury-ner"
NER_PIPELINE = None


def get_ner_pipeline():
    """Get or create the NER pipeline (cached singleton pattern)."""
    global NER_PIPELINE
    if NER_PIPELINE is None:
        logger.info(f"Loading NER model from {MODEL_ID}")
        NER_PIPELINE = pipeline(
            "ner",
            model=MODEL_ID,
            tokenizer=MODEL_ID,
            aggregation_strategy="simple",
        ) # type: ignore
        logger.info("NER model loaded successfully")
    return NER_PIPELINE


def extract_injuries_and_status(text: str) -> tuple[list[str], str]:
    """
    Extract injuries and status from text using the sports injury NER model.

    Args:
        text: The text to analyze (e.g., article title + summary)

    Returns:
        A tuple of (injuries: list[str], status: str)
        - injuries: List of injury types extracted from the text
        - status: The primary injury status (questionable, out, doubtful, etc.)
    """
    if not text:
        return [], ""

    try:
        ner_pipeline = get_ner_pipeline()
        results = ner_pipeline(text)

        injuries: set[str] = set()
        status = ""
        status_scores: dict[str, float] = {}

        for entity in results:
            entity_group = entity.get("entity_group", "")
            word = entity.get("word", "")
            score = entity.get("score", 0.0)

            # Extract injuries
            if entity_group == "INJURY" and word:
                injuries.add(word)

            # Extract status (keep track of scores to pick the highest confidence)
            elif entity_group == "STATUS" and word:
                if status_scores.get(word, 0) < score:
                    status_scores[word] = score

        # Pick the status with highest confidence
        if status_scores:
            status = max(status_scores, key=lambda k: status_scores[k])

        logger.debug(
            f"Extracted from text: injuries={sorted(injuries)}, status={status}"
        )
        return sorted(injuries), status

    except Exception as e:
        logger.error(f"Error extracting injuries/status: {e}")
        return [], ""
