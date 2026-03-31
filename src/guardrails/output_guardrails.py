"""
Output Guardrails
Prevents hallucinations, unsafe financial advice, misleading responses.
"""

import re
from src.utils.logger import get_logger

logger = get_logger(__name__)


class OutputGuardrails:
    """
    Validates agent outputs before returning to user.
    Prevents: hallucinated data, guaranteed return claims, unsafe advice.
    """

    # Patterns that indicate dangerous/misleading financial claims
    UNSAFE_CLAIM_PATTERNS = [
        (r"guarantee[sd]?\s+(a\s+)?[\d]+%|(guarantee[sd]?\s+(return|profit|gain|income))", "guaranteed returns claim"),
        (r"(100%|certain(ly)?|definitely)\s+(profit|gain|return|safe)", "certainty claim"),
        (r"risk[\s-]free\s+(investment|return|profit)", "risk-free claim"),
        (r"you\s+(will|can)\s+(definitely|certainly|always)\s+(make|earn|gain)", "certainty of profit"),
        (r"(double|triple)\s+your\s+(money|investment)\s+in", "unrealistic return claim"),
    ]

    # Fabricated data markers (model sometimes invents specific numbers)
    SUSPICIOUS_SPECIFICITY_PATTERNS = [
        r"\$[\d,]+\.\d{2}\s+per\s+share\s+by\s+\d{4}",  # precise future price prediction
        r"will\s+(reach|hit|touch)\s+\$[\d,]+\s+by\s+(next|this)\s+(month|week|year)",
    ]

    # Required disclaimer for investment advice
    DISCLAIMER_TRIGGER_PATTERNS = [
        r"(should|recommend|suggest|advise).{0,30}(invest|buy|sell|hold)",
        r"(invest|buy|sell|hold).{0,20}(should|recommend)",
        r"portfolio\s+(allocation|recommendation|advice)",
        r"is\s+(it\s+)?(good|bad|right|wise)\s+to\s+(invest|buy|sell)",
    ]

    DISCLAIMER = "\n\n⚠️ **Disclaimer**: This analysis is for informational purposes only and does not constitute personalized financial advice. Past performance is not indicative of future results. Please consult a licensed financial advisor before making investment decisions."

    def check(self, output: str, original_query: str = "") -> dict:
        """
        Validate output. Returns {safe: bool, reason, message, sanitized}.
        """
        output_lower = output.lower()

        # Check for unsafe financial claims
        for pattern, label in self.UNSAFE_CLAIM_PATTERNS:
            if re.search(pattern, output_lower, re.IGNORECASE):
                logger.warning(f"Unsafe output claim detected: {label}")
                return {
                    "safe": False,
                    "reason": "unsafe_financial_claim",
                    "message": f"⚠️ The generated response contained potentially misleading financial claims ({label}). I cannot provide guaranteed return predictions or risk-free investment guarantees. Please ask about general financial analysis instead.",
                }

        # Check for suspicious future price specificity
        for pattern in self.SUSPICIOUS_SPECIFICITY_PATTERNS:
            if re.search(pattern, output_lower, re.IGNORECASE):
                logger.warning("Suspicious future price prediction detected in output")
                return {
                    "safe": False,
                    "reason": "hallucinated_prediction",
                    "message": "⚠️ The response contained a specific future price prediction, which cannot be reliably made. I can only provide current data and general analysis.",
                }

        # Add disclaimer if giving investment-related analysis
        sanitized = output
        for pattern in self.DISCLAIMER_TRIGGER_PATTERNS:
            if re.search(pattern, output_lower, re.IGNORECASE) or re.search(pattern, original_query.lower(), re.IGNORECASE):
                if "disclaimer" not in output_lower and "not constitute" not in output_lower:
                    sanitized = output + self.DISCLAIMER
                break

        return {"safe": True, "reason": None, "message": None, "sanitized": sanitized}
