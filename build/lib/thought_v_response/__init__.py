"""thought-v-response — conversation-level, evidence-backed drift benchmark.

Built on open-mind's Comparator. Every per-turn score is decomposed into the
exact phrases that produced it. A lexical drift proxy, not an honesty score.
"""
from .evidence import benchmark, evaluate_turn, render_turn, TurnEvidence
__all__ = ["benchmark", "evaluate_turn", "render_turn", "TurnEvidence"]
__version__ = "0.1.0"
