from ..schemas.video import MetricWeights


async def get_metric_weights(user_id: int) -> MetricWeights:
    """Return default equal weights."""
    return MetricWeights()


async def set_metric_weights(user_id: int, weights: MetricWeights) -> bool:
    """Validate weights sum to 1.0."""
    total = (
        weights.fillers_weight + weights.pause_rate_weight +
        weights.emotion_weight + weights.energy_weight +
        weights.eye_contact_weight + weights.grammar_weight
    )
    if abs(total - 1.0) > 0.01:
        raise ValueError(f"Weights must sum to 1.0, but sum to {total}")
    return True