"""
Calculator Tool
Performs financial calculations: ROI, compound interest, P/E ratio, etc.
"""

import math
from src.utils.logger import get_logger

logger = get_logger(__name__)


class CalculatorTool:
    """Financial calculator with common formulas."""

    def run(self, params: dict) -> dict:
        """
        Route to the appropriate calculation.
        Params must include 'operation' key.
        """
        operation = params.get("operation", "").lower()

        try:
            if operation == "compound_interest":
                return self._compound_interest(params)
            elif operation == "roi":
                return self._roi(params)
            elif operation == "pe_ratio":
                return self._pe_ratio(params)
            elif operation == "moving_average":
                return self._moving_average(params)
            elif operation == "percentage_change":
                return self._percentage_change(params)
            elif operation == "loan_emi":
                return self._loan_emi(params)
            elif operation == "npv":
                return self._npv(params)
            elif operation == "evaluate":
                return self._safe_evaluate(params)
            else:
                return {"error": f"Unknown operation: {operation}. Supported: compound_interest, roi, pe_ratio, moving_average, percentage_change, loan_emi, npv, evaluate"}
        except Exception as e:
            logger.error(f"Calculator error: {e}")
            return {"error": str(e)}

    def _compound_interest(self, p: dict) -> dict:
        principal = float(p["principal"])
        rate = float(p["annual_rate_percent"]) / 100
        years = float(p["years"])
        n = int(p.get("compounds_per_year", 1))
        amount = principal * (1 + rate / n) ** (n * years)
        interest = amount - principal
        return {
            "principal": principal,
            "final_amount": round(amount, 2),
            "total_interest": round(interest, 2),
            "effective_rate": f"{round((amount/principal - 1)*100, 2)}%",
        }

    def _roi(self, p: dict) -> dict:
        cost = float(p["initial_investment"])
        gain = float(p["final_value"])
        roi = ((gain - cost) / cost) * 100
        return {
            "initial_investment": cost,
            "final_value": gain,
            "roi_percent": round(roi, 2),
            "net_profit": round(gain - cost, 2),
        }

    def _pe_ratio(self, p: dict) -> dict:
        price = float(p["stock_price"])
        eps = float(p["earnings_per_share"])
        if eps == 0:
            return {"error": "EPS cannot be zero"}
        pe = price / eps
        return {
            "stock_price": price,
            "eps": eps,
            "pe_ratio": round(pe, 2),
            "interpretation": "Overvalued vs market avg" if pe > 25 else ("Fair value" if pe > 15 else "Potentially undervalued"),
        }

    def _moving_average(self, p: dict) -> dict:
        prices = [float(x) for x in p["prices"]]
        window = int(p.get("window", 5))
        if len(prices) < window:
            return {"error": f"Need at least {window} prices for {window}-period MA"}
        ma = sum(prices[-window:]) / window
        return {
            "window": window,
            "moving_average": round(ma, 2),
            "latest_price": prices[-1],
            "signal": "Above MA (bullish)" if prices[-1] > ma else "Below MA (bearish)",
        }

    def _percentage_change(self, p: dict) -> dict:
        old = float(p["old_value"])
        new = float(p["new_value"])
        if old == 0:
            return {"error": "Old value cannot be zero"}
        change = ((new - old) / old) * 100
        return {
            "old_value": old,
            "new_value": new,
            "percentage_change": round(change, 2),
            "direction": "increase" if change > 0 else "decrease",
        }

    def _loan_emi(self, p: dict) -> dict:
        principal = float(p["principal"])
        annual_rate = float(p["annual_rate_percent"]) / 100
        months = int(p["tenure_months"])
        monthly_rate = annual_rate / 12
        if monthly_rate == 0:
            emi = principal / months
        else:
            emi = principal * monthly_rate * (1 + monthly_rate) ** months / ((1 + monthly_rate) ** months - 1)
        total = emi * months
        return {
            "principal": principal,
            "emi": round(emi, 2),
            "total_payment": round(total, 2),
            "total_interest": round(total - principal, 2),
        }

    def _npv(self, p: dict) -> dict:
        rate = float(p["discount_rate_percent"]) / 100
        cash_flows = [float(x) for x in p["cash_flows"]]
        initial = float(p.get("initial_investment", 0))
        npv = -initial + sum(cf / (1 + rate) ** (i + 1) for i, cf in enumerate(cash_flows))
        return {
            "npv": round(npv, 2),
            "decision": "Accept (positive NPV)" if npv > 0 else "Reject (negative NPV)",
        }

    def _safe_evaluate(self, p: dict) -> dict:
        """Safely evaluate a simple math expression."""
        expr = p.get("expression", "")
        # Only allow safe characters
        if not all(c in "0123456789+-*/.() " for c in expr):
            return {"error": "Invalid characters in expression. Use only numbers and basic operators."}
        try:
            result = eval(expr, {"__builtins__": {}}, {"sqrt": math.sqrt, "pow": math.pow})
            return {"expression": expr, "result": round(float(result), 6)}
        except Exception as e:
            return {"error": f"Could not evaluate: {e}"}
