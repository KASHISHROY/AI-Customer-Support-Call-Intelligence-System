from transformers import pipeline

_sentiment_pipeline = None

def _get_pipeline():
    global _sentiment_pipeline
    if _sentiment_pipeline is None:
        # This model is specifically trained on customer reviews
        # and understands neutral business language much better
        _sentiment_pipeline = pipeline(
            "text-classification",
            model="cardiffnlp/twitter-roberta-base-sentiment-latest"
        )
    return _sentiment_pipeline


def analyze(text: str) -> dict:
    """
    Returns sentiment and confidence for a piece of text.
    Uses RoBERTa model trained on real social/customer text.
    Outputs: POSITIVE, NEGATIVE, or NEUTRAL properly.
    """
    pipe = _get_pipeline()

    # Trim to 512 characters
    trimmed = text[:512]

    output = pipe(trimmed)[0]

    # This model returns: positive / negative / neutral directly
    label = output["label"].upper()
    score = round(output["score"], 4)

    return {
        "sentiment": label,
        "confidence": score
    }