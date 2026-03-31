"""
Financial Assistant Agent
Primary agent that handles financial queries with reasoning and tool use.
"""

import json
import re
from typing import Any
from src.tools.calculator import CalculatorTool
from src.tools.retrieval import RetrievalTool
from src.tools.market_data import MarketDataTool
from src.guardrails.input_guardrails import InputGuardrails
from src.guardrails.output_guardrails import OutputGuardrails
from src.guardrails.behavioral_guardrails import BehavioralGuardrails
from src.utils.llm_client import LLMClient
from src.utils.logger import get_logger

logger = get_logger(__name__)


class FinancialAgent:
    """
    Primary Financial Assistant Agent with guardrails.
    Handles investment queries, portfolio analysis, financial calculations,
    and market data retrieval.
    """

    SYSTEM_PROMPT = """You are a knowledgeable Financial Assistant AI. Your role is to:
1. Answer financial questions with accuracy and clarity
2. Perform financial calculations and analysis
3. Provide investment insights based on data (not personalized advice)
4. Always cite data sources and acknowledge uncertainty

You have access to these tools:
- calculator: Perform mathematical and financial calculations
- market_data: Get stock prices, market trends, financial metrics
- retrieval: Search financial knowledge base for concepts and definitions

IMPORTANT RULES:
- Always use tools when you need data or calculations
- Show your reasoning step by step
- Never fabricate financial data
- Always recommend consulting a licensed financial advisor for personal decisions
- Be honest about the limitations of your analysis

When using a tool, respond EXACTLY in this JSON format:
{"tool": "tool_name", "input": {"param": "value"}}

When you have a final answer, respond with:
{"final_answer": "your complete answer here"}

Think step by step before answering."""

    def __init__(self):
        self.llm = LLMClient()
        self.tools = {
            "calculator": CalculatorTool(),
            "market_data": MarketDataTool(),
            "retrieval": RetrievalTool(),
        }
        self.input_guard = InputGuardrails()
        self.output_guard = OutputGuardrails()
        self.behavioral_guard = BehavioralGuardrails()
        self.max_iterations = 6

    def run(self, user_query: str) -> dict[str, Any]:
        """
        Main entry point. Applies guardrails and runs the agent loop.
        Returns a structured response dict.
        """
        logger.info(f"Processing query: {user_query[:100]}...")

        # --- INPUT GUARDRAILS ---
        input_check = self.input_guard.check(user_query)
        if not input_check["safe"]:
            logger.warning(f"Input blocked: {input_check['reason']}")
            return {
                "status": "blocked",
                "guardrail": "input",
                "reason": input_check["reason"],
                "response": input_check["message"],
                "reasoning_steps": [],
            }

        # --- BEHAVIORAL GUARDRAILS (domain check) ---
        domain_check = self.behavioral_guard.check_domain(user_query)
        if not domain_check["allowed"]:
            logger.warning(f"Domain violation: {domain_check['reason']}")
            return {
                "status": "blocked",
                "guardrail": "behavioral",
                "reason": domain_check["reason"],
                "response": domain_check["message"],
                "reasoning_steps": [],
            }

        # --- AGENT LOOP ---
        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": user_query},
        ]
        reasoning_steps = []

        for iteration in range(self.max_iterations):
            logger.debug(f"Agent iteration {iteration + 1}")
            response_text = self.llm.complete(messages)

            # Parse the response
            parsed = self._parse_response(response_text)

            if parsed is None:
                # Fallback: treat as final answer
                final_answer = response_text
                break

            if "tool" in parsed:
                tool_name = parsed["tool"]
                tool_input = parsed.get("input", {})
                step = {"step": iteration + 1, "type": "tool_call", "tool": tool_name, "input": tool_input}

                if tool_name not in self.tools:
                    tool_result = f"Error: Unknown tool '{tool_name}'"
                else:
                    tool_result = self.tools[tool_name].run(tool_input)

                step["result"] = tool_result
                reasoning_steps.append(step)
                logger.debug(f"Tool {tool_name} result: {str(tool_result)[:200]}")

                messages.append({"role": "assistant", "content": response_text})
                messages.append({"role": "user", "content": f"Tool result: {json.dumps(tool_result)}"})

            elif "final_answer" in parsed:
                final_answer = parsed["final_answer"]
                reasoning_steps.append({"step": iteration + 1, "type": "final_answer"})
                break
        else:
            final_answer = "I was unable to complete the analysis within the allowed steps. Please try a more specific question."

        # --- OUTPUT GUARDRAILS ---
        output_check = self.output_guard.check(final_answer, user_query)
        if not output_check["safe"]:
            logger.warning(f"Output blocked: {output_check['reason']}")
            return {
                "status": "blocked",
                "guardrail": "output",
                "reason": output_check["reason"],
                "response": output_check["message"],
                "reasoning_steps": reasoning_steps,
            }

        final_answer = output_check.get("sanitized", final_answer)

        logger.info("Query processed successfully")
        return {
            "status": "success",
            "response": final_answer,
            "reasoning_steps": reasoning_steps,
        }

    def _parse_response(self, text: str) -> dict | None:
        """Extract JSON from LLM response."""
        # Try to find JSON block
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass
        return None
