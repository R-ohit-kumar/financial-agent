"""
Behavioral Guardrails
Enforces domain restriction (finance-only) and refusal policies.
"""

import re
from src.utils.logger import get_logger

logger = get_logger(__name__)


class BehavioralGuardrails:
    """
    Restricts agent to the financial domain.
    Blocks off-topic queries and enforces refusal policies.
    """

    # Topics that are clearly in the finance domain
    FINANCE_KEYWORDS = [
        "stock", "share", "equity", "bond", "etf", "fund", "invest", "portfolio",
        "dividend", "return", "yield", "market", "trading", "price", "valuation",
        "p/e", "eps", "revenue", "profit", "loss", "asset", "liability", "balance sheet",
        "income statement", "cash flow", "debt", "interest rate", "inflation",
        "gdp", "economy", "financial", "finance", "money", "capital", "crypto",
        "bitcoin", "currency", "forex", "commodity", "gold", "silver", "oil",
        "mutual fund", "index", "s&p", "nasdaq", "dow", "nifty", "sensex",
        "ipo", "earnings", "quarter", "annual report", "rsi", "moving average",
        "risk", "hedge", "option", "future", "derivative", "budget", "savings",
        "expense", "loan", "mortgage", "credit", "tax", "retirement", "401k",
        "ira", "pension", "insurance", "net worth", "compound interest", "roi",
        "profit margin", "ebitda", "roe", "roa", "book value", "market cap",
        "bear market", "bull market", "recession", "correction", "volatility",
    ]

    # Topics that are clearly off-domain
    OFF_DOMAIN_INDICATORS = [
        (r"\b(recipe|cooking|baking|ingredient)\b", "cooking"),
        (r"\b(movie|film|actor|actress|director|netflix|watch)\b", "entertainment"),
        (r"\b(song|music|album|artist|spotify|playlist)\b", "music"),
        (r"\b(game|gaming|playstation|xbox|nintendo|fortnite)\b", "gaming"),
        (r"\b(dating|relationship|girlfriend|boyfriend|marriage)\b", "relationships"),
        (r"\b(weather|forecast|temperature|rain|snow|climate)\b", "weather"),
        (r"\b(medical|diagnosis|symptom|disease|treatment|medication|doctor)\b", "medical"),
        (r"\b(homework|essay|history|geography|science\s+project)\b", "academic"),
        (r"\b(travel|hotel|flight|vacation|tourism|sightseeing)\b", "travel"),
        (r"\b(code|programming|python|javascript|debug|software)\b.{0,20}(?!stock|finance|trading)", "programming"),
    ]

    # Minimum finance signal threshold
    MIN_FINANCE_SIGNALS = 1

    def check_domain(self, query: str) -> dict:
        """
        Check if query is within the financial domain.
        Returns {allowed: bool, reason: str, message: str}.
        """
        query_lower = query.lower()

        # Count finance keyword matches
        finance_signals = sum(1 for kw in self.FINANCE_KEYWORDS if kw in query_lower)

        # Check for off-domain indicators
        for pattern, domain in self.OFF_DOMAIN_INDICATORS:
            if re.search(pattern, query_lower, re.IGNORECASE):
                # Only block if no financial context
                if finance_signals < self.MIN_FINANCE_SIGNALS:
                    logger.info(f"Off-domain query blocked: domain={domain}")
                    return {
                        "allowed": False,
                        "reason": f"off_domain_{domain}",
                        "message": f"🏦 I'm a specialized **Financial Assistant** and can only help with financial topics such as stocks, investments, portfolio analysis, market data, and financial calculations.\n\nIt looks like your question is about **{domain}**, which is outside my domain. Please ask me about financial matters!",
                    }

        # If no finance signals at all and query is substantive, flag it
        if finance_signals == 0 and len(query.split()) > 4:
            # Check if it might still be a general financial question by context
            general_financial_contexts = [
                r"(how|what|why|when|where|should|can|is|are).{0,30}(worth|value|cost|price|afford|pay|earn|make money)",
                r"(what|how).{0,20}(compound|interest|percentage|rate|calculate)",
            ]
            is_contextually_financial = any(
                re.search(p, query_lower) for p in general_financial_contexts
            )

            if not is_contextually_financial:
                return {
                    "allowed": False,
                    "reason": "no_financial_context",
                    "message": "🏦 I'm a **Financial Assistant** specialized in financial topics. Your question doesn't seem to be related to finance, investments, or economics. Please ask me about stocks, budgeting, investments, market data, or financial analysis!",
                }

        return {"allowed": True, "reason": None, "message": None}

    def check_refusal_policy(self, query: str) -> dict:
        """
        Check if query requires a policy-based refusal.
        """
        query_lower = query.lower()

        # Personalized legal advice refusal
        if re.search(r"(is\s+this\s+legal|legal\s+advice|lawsuit|sue|court)", query_lower):
            return {
                "allowed": False,
                "reason": "legal_advice_request",
                "message": "I cannot provide legal advice. Please consult a qualified attorney for legal questions related to financial matters.",
            }

        return {"allowed": True, "reason": None, "message": None}
