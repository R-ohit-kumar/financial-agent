"""
Financial Assistant AI Agent - Main Entry Point
Run: python main.py
Or with a query: python main.py "What is Apple's P/E ratio?"
"""

import sys
import json
from src.agents.financial_agent import FinancialAgent
from dotenv import load_dotenv
load_dotenv()


def print_response(result: dict):
    print("\n" + "="*60)
    status = result.get("status", "unknown")

    if status == "blocked":
        guardrail = result.get("guardrail", "unknown")
        print(f"🛡️  GUARDRAIL TRIGGERED [{guardrail.upper()}]")
        print(f"Reason: {result.get('reason', 'N/A')}")
        print(f"\n{result.get('response', '')}")
    else:
        print("✅ RESPONSE:")
        print(result.get("response", "No response"))

    steps = result.get("reasoning_steps", [])
    if steps:
        print(f"\n📊 Reasoning Steps ({len(steps)}):")
        for s in steps:
            if s.get("type") == "tool_call":
                print(f"  [{s['step']}] Tool: {s['tool']} → {json.dumps(s['result'])[:120]}...")
            else:
                print(f"  [{s['step']}] Final answer generated")

    print("="*60 + "\n")


def interactive_mode(agent: FinancialAgent):
    print("\n🏦 Financial Assistant Agent")
    print("Type your financial question, or 'quit' to exit.\n")

    while True:
        try:
            query = input("You: ").strip()
            if query.lower() in ("quit", "exit", "q"):
                print("Goodbye!")
                break
            if not query:
                continue
            result = agent.run(query)
            print_response(result)
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break


def main():
    agent = FinancialAgent()

    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        print(f"Query: {query}")
        result = agent.run(query)
        print_response(result)
    else:
        interactive_mode(agent)


if __name__ == "__main__":
    main()
