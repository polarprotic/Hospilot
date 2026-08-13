"""
Diagnostic Resource Allocation Service for HOSPILOT.

Loads and registers configuration artifacts for diagnostic resources (MRI, CT Scan, Lab),
and executes multi-agent RL auction bidding for scarce diagnostic slots.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional


CONFIG_DIR = Path(__file__).resolve().parent.parent.parent / "config"


def load_diagnostic_profile() -> Dict[str, Any]:
    """Loads the diagnostic resource profile configuration."""
    profile_path = CONFIG_DIR / "diagnostic_profile.json"
    with open(profile_path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_diagnostic_caps() -> Dict[str, Any]:
    """Loads the diagnostic resource utility caps configuration."""
    caps_path = CONFIG_DIR / "diagnostic_caps.json"
    with open(caps_path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_diagnostic_budget() -> Dict[str, Any]:
    """Loads the diagnostic resource budget configuration."""
    budget_path = CONFIG_DIR / "diagnostic_budget.json"
    with open(budget_path, "r", encoding="utf-8") as f:
        return json.load(f)


class DiagnosticResourceEngine:
    """HOSPILOT Diagnostic Resource Allocation Engine."""

    def __init__(self):
        self.profile = load_diagnostic_profile()
        self.caps = load_diagnostic_caps()
        self.budget_config = load_diagnostic_budget()

    def get_registered_profile(self) -> Dict[str, Any]:
        return self.profile

    def calculate_utility(
        self,
        clinical_benefit: float,
        urgency: float,
        delay_impact: float,
        throughput_impact: float,
        operational_impact: float,
        financial_impact: float,
        alternative_penalty: float = 0.0,
        resource_stress_penalty: float = 0.0,
    ) -> float:
        """Calculates utility score capped according to diagnostic_caps.json configuration."""
        raw_utility = (
            min(clinical_benefit, 60.0)
            + min(urgency, 40.0)
            + min(delay_impact, 25.0)
            + min(throughput_impact, 25.0)
            + min(operational_impact, 20.0)
            + min(financial_impact, 10.0)
            + max(alternative_penalty, -20.0)
            + max(resource_stress_penalty, -10.0)
        )
        return max(0.0, min(raw_utility, 200.0))

    def calculate_budget_cost(
        self,
        bid: float,
        contention_factor: float = 1.0,
        won: bool = True,
        commitment_rate: float = 0.25,
    ) -> float:
        """Calculates permanent budget deduction cost for an agent bid."""
        outcome_factor = 1.0 if won else 0.10
        return bid * contention_factor * outcome_factor * commitment_rate


def register_diagnostic_resource():
    """Profile registration function called by HOSPILOT core runtime."""
    engine = DiagnosticResourceEngine()
    return {
        "status": "REGISTERED",
        "resource_id": engine.profile["resource_id"],
        "modalities": engine.profile["modalities"],
        "registered_agents": [agent["agent_id"] for agent in engine.profile["bidding_agents"]],
    }
