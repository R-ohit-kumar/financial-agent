"""
Input Guardrails
Detects: prompt injection, harmful queries, irrelevant queries.
"""

import re
from src.utils.logger import get_logger

logger = get_logger(__name__)


class InputGuardrails:
    """
    Validates user inputs before they reach the agent.
    Blocks: prompt injection, harmful content, jailbreak attempts.
    """

    # Prompt injection patterns
    INJECTION_PATTERNS = [
        r"ignore\s+(all\s+)?(previous|prior|above)\s+instructions",
        r"disregard\s+(your\s+)?(system\s+)?prompt",
        r"you\s+are\s+now\s+(a\s+)?(?!a financial)",
        r"pretend\s+(you\s+are|to\s+be)",
        r"act\s+as\s+(if\s+you\s+(are|were)|a)",
        r"jailbreak",
        r"DAN\s+mode",
        r"developer\s+mode",
        r"override\s+(safety|guardrail|filter)",
        r"forget\s+(your\s+)?(training|instructions|rules)",
        r"new\s+instructions\s*:",
        r"system\s*:\s*you\s+are",
        r"\[SYSTEM\]",
        r"<\s*system\s*>",
    ]

    # Harmful content patterns
    HARMFUL_PATTERNS = [
        r"\b(fraud|scam|ponzi|pyramid\s+scheme)\b",
        r"money\s+laundering",
        r"tax\s+evasion",
        r"insider\s+trading.{0,20}(how|advice|tips)",
        r"pump\s+and\s+dump",
        r"market\s+manipulation",
        r"(steal|hack)\s+.{0,20}(account|money|funds)",
    ]

    # Max query length
    MAX_LENGTH = 2000

    def check(self, query: str) -> dict:
        """
        Run all input checks. Returns {safe: bool, reason: str, message: str}.
        """
        # Length check
        if len(query) > self.MAX_LENGTH:
            return {
                "safe": False,
                "reason": "query_too_long",
                "message": f"Your query is too long ({len(query)} chars). Please keep it under {self.MAX_LENGTH} characters.",
            }

        # Empty check
        if not query.strip():
            return {
                "safe": False,
                "reason": "empty_query",
                "message": "Please enter a question or query.",
            }

        query_lower = query.lower()

        # Prompt injection check
        for pattern in self.INJECTION_PATTERNS:
            if re.search(pattern, query_lower, re.IGNORECASE):
                logger.warning(f"Prompt injection detected: pattern={pattern}")
                return {
                    "safe": False,
                    "reason": "prompt_injection",
                    "message": "⚠️ Potentially unsafe instruction detected. I can only follow my built-in guidelines as a financial assistant. Please ask a genuine financial question.",
                }

        # Harmful content check
        for pattern in self.HARMFUL_PATTERNS:
            if re.search(pattern, query_lower, re.IGNORECASE):
                logger.warning(f"Harmful content detected: pattern={pattern}")
                return {
                    "safe": False,
                    "reason": "harmful_content",
                    "message": "⚠️ I cannot assist with queries related to financial fraud, market manipulation, or illegal financial activities. Please ask about legitimate financial topics.",
                }

        return {"safe": True, "reason": None, "message": None}
