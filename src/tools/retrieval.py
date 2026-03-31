"""
Retrieval Tool
Searches a mock financial knowledge base for concepts and definitions.
"""

import re
from src.utils.logger import get_logger

logger = get_logger(__name__)


KNOWLEDGE_BASE = {
    "pe_ratio": {
        "title": "Price-to-Earnings (P/E) Ratio",
        "content": "The P/E ratio measures how much investors pay per dollar of earnings. Formula: Stock Price / EPS. A high P/E (>25) may indicate overvaluation or high growth expectations. Low P/E (<15) may indicate undervaluation or low growth. Compare within the same sector for meaningful analysis.",
        "tags": ["valuation", "metric", "fundamental"],
    },
    "compound_interest": {
        "title": "Compound Interest",
        "content": "Compound interest is interest calculated on both the initial principal and the accumulated interest. Formula: A = P(1 + r/n)^(nt). It's often called the 'eighth wonder of the world' for its power in long-term wealth building. Higher compounding frequency = slightly more returns.",
        "tags": ["interest", "savings", "investment"],
    },
    "diversification": {
        "title": "Portfolio Diversification",
        "content": "Diversification is spreading investments across different asset classes, sectors, and geographies to reduce risk. A diversified portfolio reduces unsystematic (company-specific) risk. Recommended allocation: 60-70% equities, 20-30% bonds, 5-10% alternatives for moderate risk profiles.",
        "tags": ["risk", "portfolio", "strategy"],
    },
    "dollar_cost_averaging": {
        "title": "Dollar-Cost Averaging (DCA)",
        "content": "DCA is an investment strategy of investing a fixed amount at regular intervals regardless of price. Benefits: reduces impact of volatility, removes emotional decision-making, accessible for beginners. Best for long-term investors who can't time the market.",
        "tags": ["strategy", "investment", "risk management"],
    },
    "rsi": {
        "title": "Relative Strength Index (RSI)",
        "content": "RSI is a momentum oscillator measuring speed and magnitude of price changes on a scale of 0-100. RSI > 70: Overbought (potential sell signal). RSI < 30: Oversold (potential buy signal). RSI 40-60: Neutral. It's a lagging indicator; use with other signals.",
        "tags": ["technical analysis", "indicator", "momentum"],
    },
    "market_cap": {
        "title": "Market Capitalization",
        "content": "Market cap = Share Price × Total Shares Outstanding. Categories: Large-cap (>$10B): stable, lower risk. Mid-cap ($2B-$10B): balance of growth and stability. Small-cap (<$2B): higher growth potential, higher risk. It determines index inclusion and institutional investment eligibility.",
        "tags": ["valuation", "classification", "metric"],
    },
    "bull_bear_market": {
        "title": "Bull vs Bear Markets",
        "content": "Bull Market: Sustained rise of 20%+ from recent lows, characterized by optimism and economic expansion. Bear Market: Decline of 20%+ from recent highs, characterized by pessimism. Historical avg bull market: ~6.6 years. Historical avg bear market: ~1.3 years.",
        "tags": ["market", "cycles", "terminology"],
    },
    "etf": {
        "title": "Exchange-Traded Fund (ETF)",
        "content": "ETFs are investment funds traded on stock exchanges. They track an index, sector, commodity, or asset. Benefits: Low expense ratios, diversification, tax efficiency, liquidity. Popular: SPY (S&P 500), QQQ (NASDAQ 100), VTI (Total Market). Preferred by passive investors.",
        "tags": ["investment vehicle", "passive", "index"],
    },
    "debt_to_equity": {
        "title": "Debt-to-Equity Ratio",
        "content": "D/E Ratio = Total Debt / Shareholders' Equity. Measures financial leverage. < 1.0: Conservative, lower risk. 1.0-2.0: Moderate leverage. > 2.0: High leverage, higher risk. Varies by sector (banks naturally have higher D/E). Compare within the same industry.",
        "tags": ["leverage", "risk", "fundamental"],
    },
    "inflation": {
        "title": "Inflation and Investments",
        "content": "Inflation erodes purchasing power over time. Real return = Nominal return - Inflation. Inflation-beating investments: equities (historically ~7% real returns), real estate, commodities, TIPS (Treasury Inflation-Protected Securities). Cash and low-yield bonds lose real value during high inflation.",
        "tags": ["macroeconomics", "risk", "real return"],
    },
    "sip": {
        "title": "Systematic Investment Plan (SIP)",
        "content": "SIP is an investment method where a fixed amount is invested in mutual funds at regular intervals (monthly/quarterly). Benefits: Rupee cost averaging, disciplined investing, compounding benefits. Popular in India. Minimum SIP amounts as low as ₹500/month in Indian mutual funds.",
        "tags": ["india", "mutual fund", "investment strategy"],
    },
    "nifty_sensex": {
        "title": "NIFTY 50 and SENSEX",
        "content": "NIFTY 50 is NSE's benchmark index of 50 large-cap Indian companies. SENSEX is BSE's index of 30 blue-chip companies. Both reflect the health of the Indian economy. Historical CAGR: ~12-15% over 20 years. Used as benchmarks for Indian mutual funds and ETFs.",
        "tags": ["india", "index", "market"],
    },
}


class RetrievalTool:
    """Searches the financial knowledge base."""

    def run(self, params: dict) -> dict:
        query = params.get("query", "").lower()
        if not query:
            return {"error": "No query provided"}

        results = []
        query_words = set(query.split())

        for key, entry in KNOWLEDGE_BASE.items():
            score = 0
            text = (entry["title"] + " " + entry["content"] + " " + " ".join(entry["tags"])).lower()

            # Exact phrase match
            if query in text:
                score += 10

            # Keyword overlap
            text_words = set(re.findall(r'\w+', text))
            overlap = query_words & text_words
            score += len(overlap) * 2

            # Tag match
            for tag in entry["tags"]:
                if tag in query or query in tag:
                    score += 5

            if score > 0:
                results.append({"score": score, "key": key, **entry})

        results.sort(key=lambda x: x["score"], reverse=True)
        top = results[:3]

        if not top:
            return {
                "message": "No specific knowledge found for this query.",
                "suggestion": "Try terms like: P/E ratio, compound interest, diversification, RSI, ETF, SIP, inflation",
            }

        return {
            "results": [{"title": r["title"], "content": r["content"], "tags": r["tags"]} for r in top],
            "count": len(top),
        }
