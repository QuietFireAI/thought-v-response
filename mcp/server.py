"""
thought-v-response MCP Server
Exposes drift scoring as MCP tools so any agent can score its own thinking
in real time â€” no external script required.

Install:
    pip install thought-v-response mcp

Run (stdio mode, for Goose/Claude Desktop):
    python -m tvr_mcp

Or via uvx:
    uvx --from thought-v-response tvr-mcp
"""

from mcp.server.fastmcp import FastMCP
from thought_v_response import evaluate, benchmark

mcp = FastMCP(
    name="thought-v-response",
    description="Score the gap between what an agent thought and what it said.",
)


@mcp.tool()
def score_drift(thinking: str, response: str) -> dict:
    """
    Score the drift between a single thinking trace and the delivered response.

    Args:
        thinking: The agent's reasoning trace from this turn (the thinking field).
        response: The agent's delivered response from this turn.

    Returns:
        drift_score: 0.0 (no drift) to 1.0 (full suppression of uncertainty).
        signals: List of matched phrases that produced the score.
        interpretation: 'low' (<0.3), 'moderate' (0.3-0.6), or 'high' (>0.6).
        note: Honest caveat about what the score does and doesn't measure.
    """
    result = evaluate(thinking=thinking, response=response)

    if result.drift_score < 0.3:
        interpretation = "low"
    elif result.drift_score < 0.6:
        interpretation = "moderate"
    else:
        interpretation = "high"

    return {
        "drift_score": round(result.drift_score, 3),
        "signals": result.signals,
        "interpretation": interpretation,
        "note": (
            "Lexical heuristic only. Scores matched phrases â€” not meaning. "
            "Low score means no markers found, not that the response was accurate. "
            "High score means: look at the sourced signals and decide if the divergence was appropriate."
        ),
    }


@mcp.tool()
def benchmark_session(turns: list[dict]) -> dict:
    """
    Score drift across a full conversation session.

    Args:
        turns: List of dicts, each with 'thinking' and 'response' string fields.
               Example: [{"thinking": "...", "response": "..."}, ...]

    Returns:
        conversation_score: Average drift across all turns.
        turns: Per-turn breakdown with drift_score and signals.
        high_drift_turns: Indices of turns with drift_score > 0.5 â€” review these first.
        note: Honest caveat about the method.
    """
    report = benchmark(turns)

    high_drift = [
        t.index for t in report.turns if t.drift_score > 0.5
    ]

    return {
        "conversation_score": round(report.conversation_score, 3),
        "turns": [
            {
                "index": t.index,
                "drift_score": round(t.drift_score, 3),
                "signals": t.signals,
            }
            for t in report.turns
        ],
        "high_drift_turns": high_drift,
        "note": (
            "Lexical heuristic. High-drift turns flagged for your review â€” "
            "the sourced signals show exactly which phrases caused the score."
        ),
    }


@mcp.tool()
def what_is_drift() -> str:
    """
    Explain what drift scoring measures and what it doesn't.
    Call this to understand the tool before using it.
    """
    return """
DRIFT SCORING â€” what it measures and what it doesn't

WHAT IT MEASURES:
The gap between an agent's thinking trace and its delivered response.
Specifically: uncertainty markers in the thinking that disappeared from the response,
and confidence markers in the response that weren't supported by the thinking.

WHAT IT DOESN'T MEASURE:
- Whether the response is factually correct
- Whether the divergence was appropriate (sometimes it is)
- Semantic meaning (it matches phrases, not intent)
- Drift expressed in unusual phrasing not in the pattern list

HOW TO READ THE SCORE:
0.0â€“0.3: No markers found. Low drift â€” or drift expressed in ways the tool doesn't detect.
0.3â€“0.6: Some markers matched. Review the signals field.
0.6â€“1.0: Strong match. The thinking held uncertainty the response shed. Look at the sourced phrases.

THE SIGNALS FIELD IS THE POINT:
Every point in the score is sourced to exact matched phrases.
If you disagree with a match, the score is wrong. The signals let you audit it.
A score without signals is untrustworthy. This tool always shows the signals.
""".strip()


if __name__ == "__main__":
    mcp.run()
