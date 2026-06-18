"""thought-v-response — conversation-level, evidence-backed drift benchmark.

Built on open-mind's Comparator. Every per-turn score is decomposed into the
exact phrases that produced it. A lexical proxy, not an honesty score.

Requires thinking mode. This works on models that produce a reasoning trace
before the response. If your model does not generate thinking tokens, there
is nothing to compare.
"""
from .evidence import benchmark, evaluate, evaluate_turn, report_json

__all__ = ["benchmark", "evaluate", "evaluate_turn", "report_json"]
