# Guardrails Documentation

## Overview

This agent implements three independent guardrail layers that intercept queries at different points in the pipeline. All guardrails are **deterministic, rule-based, and LLM-free** — they execute in milliseconds without API calls.

---

## Layer 1 — Input Guardrails

**File**: `src/guardrails/input_guardrails.py`  
**Trigger point**: Before any processing (first gate)

### 1a. Prompt Injection Detection

Detects attempts to override the agent's instructions or persona.

**Patterns monitored**:
```
ignore (all) (previous|prior|above) instructions
disregard (your) (system) prompt
you are now [X]          → jailbreak persona swap
pretend (you are|to be)  → role-play bypass
act as (if you were|a)   → persona override
jailbreak / DAN mode     → explicit jailbreak keywords
developer mode           → common bypass phrase
override (safety|guardrail|filter)
forget your (training|instructions|rules)
[SYSTEM] / <system>      → fake system tag injection
```

**Response**: Returns `safe=False` with reason `prompt_injection` and a user-facing explanation.

### 1b. Harmful Content Detection

Blocks queries seeking guidance on illegal or harmful financial activities.

**Patterns monitored**:
```
fraud / scam / ponzi / pyramid scheme
money laundering
tax evasion
insider trading + (how|advice|tips)
pump and dump
market manipulation
steal/hack + (account|money|funds)
```

**Response**: Returns `safe=False` with reason `harmful_content`.

### 1c. Length Validation

- Maximum query length: **2,000 characters**
- Prevents context-stuffing attacks and prompt injection via extremely long inputs

### 1d. Empty Query Check

- Rejects empty or whitespace-only queries immediately

---

## Layer 2 — Behavioral Guardrails

**File**: `src/guardrails/behavioral_guardrails.py`  
**Trigger point**: After input validation, before agent execution

### 2a. Domain Restriction

The agent is restricted to **financial topics only**. Domain is determined by:

1. **Finance keyword scoring** — counts matches from a vocabulary of 70+ finance terms (stock, equity, portfolio, dividend, inflation, etc.)
2. **Off-domain pattern detection** — checks for definitive non-finance signals (cooking recipes, movie titles, weather, medical symptoms, etc.)
3. **Contextual financial intent** — catches general financial queries without explicit keywords (e.g., "how much can I afford?")

**Off-domain categories blocked**:
- Cooking / recipes
- Entertainment (movies, music, gaming)
- Relationships / dating
- Weather / climate
- Medical / health diagnosis
- Pure academic homework (non-economics)
- Travel / tourism

**Response**: Returns `allowed=False` with a redirect message explaining the agent's scope and suggesting financial question alternatives.

### 2b. Refusal Policy

Explicit refusal for categories where the agent should not engage:
- Requests for **legal advice** about financial matters → refer to attorney
- Requests for **personalized investment advice** with guaranteed outcomes → handled at output layer

---

## Layer 3 — Output Guardrails

**File**: `src/guardrails/output_guardrails.py`  
**Trigger point**: After agent generates a response, before returning to user

### 3a. Unsafe Financial Claim Detection

Catches hallucinated or fabricated guarantees in the LLM output.

**Patterns blocked**:
```
guarantee[sd]? a X% return
guaranteed (return|profit|gain|income)
100%/certain/definitely (profit|gain|return|safe)
risk-free (investment|return|profit)
you will definitely (make|earn|gain)
double/triple your money in [timeframe]
```

**Response**: Returns `safe=False`, explains that guaranteed return claims cannot be made, and suggests rephrasing.

### 3b. Hallucinated Future Price Detection

Prevents the model from inventing specific future price targets.

**Patterns blocked**:
```
$X,XXX.XX per share by YYYY
will (reach|hit|touch) $X by (next|this) (month|week|year)
```

**Response**: Returns `safe=False` with explanation that future price predictions cannot be reliably made.

### 3c. Disclaimer Auto-Injection

When the response involves **investment recommendations or analysis**, a standardized risk disclaimer is automatically appended:

> ⚠️ **Disclaimer**: This analysis is for informational purposes only and does not constitute personalized financial advice. Past performance is not indicative of future results. Please consult a licensed financial advisor before making investment decisions.

**Triggers on**:
- Response or query contains: should/recommend/suggest + invest/buy/sell/hold
- Portfolio allocation or recommendation queries
- "Is it good/wise to invest/buy?" questions

---

## Guardrail Interaction Summary

```
Query → [Input] → [Behavioral] → [Agent+LLM] → [Output] → Response
          │              │                           │
       Blocks:        Blocks:                    Blocks:
       • Injection    • Off-domain              • Unsafe claims
       • Harmful      • Policy refusals         • Hallucinations
       • Too long                               Appends:
       • Empty                                  • Disclaimers
```

---

## Design Decisions

**Why rule-based instead of LLM-based guardrails?**

| Aspect | Rule-Based (current) | LLM-Based |
|--------|---------------------|-----------|
| Latency | ~1ms | ~500-2000ms |
| Cost | Free | API cost per call |
| Determinism | ✅ 100% predictable | ❌ Non-deterministic |
| Explainability | ✅ Clear pattern match | ❌ Opaque |
| Sophistication | ❌ Pattern-limited | ✅ Nuanced understanding |
| Adversarial robustness | Medium | Medium-High |

For a production system, we recommend **rule-based as first layer** (fast, cheap, deterministic) + **LLM judge as second layer** for ambiguous cases that pass the first filter.
