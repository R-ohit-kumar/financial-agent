"""
Market Data Tool
Provides mock stock prices, financial metrics, and market data.
In production, replace with real API (Alpha Vantage, Yahoo Finance, etc.)
"""

import random
from datetime import datetime, timedelta
from src.utils.logger import get_logger

logger = get_logger(__name__)


# Mock financial database
MOCK_STOCKS = {
    "AAPL": {
        "name": "Apple Inc.",
        "price": 189.30,
        "change_pct": 1.2,
        "market_cap": "2.95T",
        "pe_ratio": 31.2,
        "eps": 6.07,
        "dividend_yield": 0.5,
        "52w_high": 199.62,
        "52w_low": 164.08,
        "sector": "Technology",
        "revenue_ttm": "383.29B",
        "debt_to_equity": 1.87,
    },
    "MSFT": {
        "name": "Microsoft Corporation",
        "price": 415.50,
        "change_pct": 0.8,
        "market_cap": "3.08T",
        "pe_ratio": 36.4,
        "eps": 11.41,
        "dividend_yield": 0.7,
        "52w_high": 430.82,
        "52w_low": 309.45,
        "sector": "Technology",
        "revenue_ttm": "245.12B",
        "debt_to_equity": 0.35,
    },
    "GOOGL": {
        "name": "Alphabet Inc.",
        "price": 175.20,
        "change_pct": -0.5,
        "market_cap": "2.17T",
        "pe_ratio": 24.1,
        "eps": 7.27,
        "dividend_yield": 0.0,
        "52w_high": 193.31,
        "52w_low": 130.67,
        "sector": "Technology",
        "revenue_ttm": "350.02B",
        "debt_to_equity": 0.08,
    },
    "TSLA": {
        "name": "Tesla Inc.",
        "price": 245.00,
        "change_pct": -2.1,
        "market_cap": "781.4B",
        "pe_ratio": 78.2,
        "eps": 3.13,
        "dividend_yield": 0.0,
        "52w_high": 299.29,
        "52w_low": 138.80,
        "sector": "Consumer Discretionary",
        "revenue_ttm": "97.69B",
        "debt_to_equity": 0.18,
    },
    "AMZN": {
        "name": "Amazon.com Inc.",
        "price": 198.90,
        "change_pct": 1.5,
        "market_cap": "2.09T",
        "pe_ratio": 47.3,
        "eps": 4.21,
        "dividend_yield": 0.0,
        "52w_high": 201.20,
        "52w_low": 118.35,
        "sector": "Consumer Discretionary",
        "revenue_ttm": "620.13B",
        "debt_to_equity": 0.72,
    },
    "NVDA": {
        "name": "NVIDIA Corporation",
        "price": 875.40,
        "change_pct": 3.2,
        "market_cap": "2.15T",
        "pe_ratio": 65.8,
        "eps": 13.30,
        "dividend_yield": 0.03,
        "52w_high": 974.00,
        "52w_low": 373.35,
        "sector": "Technology",
        "revenue_ttm": "79.77B",
        "debt_to_equity": 0.42,
    },
    "JPM": {
        "name": "JPMorgan Chase & Co.",
        "price": 198.20,
        "change_pct": 0.3,
        "market_cap": "571.3B",
        "pe_ratio": 11.8,
        "eps": 16.80,
        "dividend_yield": 2.5,
        "52w_high": 220.82,
        "52w_low": 135.19,
        "sector": "Financials",
        "revenue_ttm": "162.40B",
        "debt_to_equity": 1.24,
    },
    "RELIANCE": {
        "name": "Reliance Industries Ltd.",
        "price": 2850.00,
        "change_pct": 0.6,
        "market_cap": "19.3T INR",
        "pe_ratio": 27.4,
        "eps": 104.01,
        "dividend_yield": 0.3,
        "52w_high": 3024.90,
        "52w_low": 2220.30,
        "sector": "Conglomerate",
        "revenue_ttm": "9.74T INR",
        "debt_to_equity": 0.39,
        "currency": "INR",
    },
    "TCS": {
        "name": "Tata Consultancy Services",
        "price": 4120.00,
        "change_pct": -0.4,
        "market_cap": "14.9T INR",
        "pe_ratio": 30.1,
        "eps": 136.90,
        "dividend_yield": 1.4,
        "52w_high": 4592.25,
        "52w_low": 3311.75,
        "sector": "Technology",
        "revenue_ttm": "2.41T INR",
        "debt_to_equity": 0.06,
        "currency": "INR",
    },
}

MARKET_INDICES = {
    "S&P 500": {"value": 5218.19, "change_pct": 0.51, "ytd": 10.2},
    "NASDAQ": {"value": 16742.39, "change_pct": 0.82, "ytd": 11.8},
    "DOW JONES": {"value": 39069.59, "change_pct": 0.20, "ytd": 5.4},
    "NIFTY 50": {"value": 22403.85, "change_pct": -0.15, "ytd": 3.1},
    "SENSEX": {"value": 73878.15, "change_pct": -0.12, "ytd": 3.5},
}

ECONOMIC_INDICATORS = {
    "US_INFLATION": {"value": 3.2, "unit": "%", "period": "March 2024"},
    "US_FED_RATE": {"value": 5.25, "unit": "%", "description": "Federal Funds Rate"},
    "US_GDP_GROWTH": {"value": 3.4, "unit": "%", "period": "Q4 2023"},
    "INDIA_INFLATION": {"value": 4.85, "unit": "%", "period": "March 2024"},
    "INDIA_REPO_RATE": {"value": 6.5, "unit": "%", "description": "RBI Repo Rate"},
    "GOLD_PRICE": {"value": 2332.50, "unit": "USD/oz"},
    "CRUDE_OIL": {"value": 85.40, "unit": "USD/barrel", "type": "Brent"},
    "USD_INR": {"value": 83.45, "unit": "INR per USD"},
}


class MarketDataTool:
    """Provides mock market data for financial analysis."""

    def run(self, params: dict) -> dict:
        query_type = params.get("type", "").lower()

        try:
            if query_type == "stock":
                return self._get_stock(params)
            elif query_type == "compare_stocks":
                return self._compare_stocks(params)
            elif query_type == "market_indices":
                return self._get_indices(params)
            elif query_type == "economic_indicators":
                return self._get_economic_indicators(params)
            elif query_type == "historical_prices":
                return self._get_historical(params)
            else:
                return {"error": f"Unknown type: {query_type}. Use: stock, compare_stocks, market_indices, economic_indicators, historical_prices"}
        except Exception as e:
            logger.error(f"MarketData error: {e}")
            return {"error": str(e)}

    def _get_stock(self, p: dict) -> dict:
        ticker = p.get("ticker", "").upper()
        if ticker not in MOCK_STOCKS:
            available = ", ".join(MOCK_STOCKS.keys())
            return {"error": f"Ticker '{ticker}' not found in mock database. Available: {available}"}
        data = MOCK_STOCKS[ticker].copy()
        data["ticker"] = ticker
        data["data_source"] = "mock_data"
        data["timestamp"] = datetime.now().strftime("%Y-%m-%d")
        return data

    def _compare_stocks(self, p: dict) -> dict:
        tickers = [t.upper() for t in p.get("tickers", [])]
        results = {}
        for ticker in tickers:
            if ticker in MOCK_STOCKS:
                results[ticker] = MOCK_STOCKS[ticker]
            else:
                results[ticker] = {"error": "Not found"}
        return {"comparison": results, "data_source": "mock_data"}

    def _get_indices(self, _: dict) -> dict:
        return {"indices": MARKET_INDICES, "timestamp": datetime.now().strftime("%Y-%m-%d")}

    def _get_economic_indicators(self, _: dict) -> dict:
        return {"indicators": ECONOMIC_INDICATORS, "timestamp": datetime.now().strftime("%Y-%m-%d")}

    def _get_historical(self, p: dict) -> dict:
        ticker = p.get("ticker", "").upper()
        days = int(p.get("days", 30))
        if ticker not in MOCK_STOCKS:
            return {"error": f"Ticker '{ticker}' not found"}
        base_price = MOCK_STOCKS[ticker]["price"]
        prices = []
        price = base_price * 0.85
        for i in range(days):
            date = (datetime.now() - timedelta(days=days - i)).strftime("%Y-%m-%d")
            price = price * (1 + random.uniform(-0.025, 0.025))
            prices.append({"date": date, "close": round(price, 2)})
        prices[-1]["close"] = base_price  # End at current price
        return {"ticker": ticker, "historical_prices": prices, "data_source": "mock_data"}
