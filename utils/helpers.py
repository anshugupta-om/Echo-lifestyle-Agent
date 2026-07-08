"""
utils/helpers.py
----------------
Miscellaneous helper functions used across the project.
"""

from __future__ import annotations

import hashlib
import random
import re
from datetime import date
from typing import Any

from prompts.agent_instructions import (
    DAILY_ECO_TIPS,
    CARBON_EMISSION_FACTORS,
    ECO_SCORE_THRESHOLDS,
)


# ── Daily Tip ────────────────────────────────────────────────

def get_daily_eco_tip() -> str:
    """Return a deterministic daily tip (changes every calendar day)."""
    seed = int(date.today().strftime("%Y%m%d"))
    random.seed(seed)
    return random.choice(DAILY_ECO_TIPS)


def get_random_tip() -> str:
    """Return a truly random tip (for refresh button)."""
    return random.choice(DAILY_ECO_TIPS)


# ── Carbon Calculator ────────────────────────────────────────

def calculate_carbon_footprint(
    *,
    electricity_kwh_per_month: float = 0,
    lpg_cylinders_per_year: float = 0,
    car_km_per_day: float = 0,
    car_fuel_type: str = "petrol",
    bike_km_per_day: float = 0,
    bus_km_per_day: float = 0,
    metro_km_per_day: float = 0,
    flights_per_year: int = 0,
    avg_flight_km: float = 1500,
    diet_type: str = "medium_meat",
    food_waste_kg_per_week: float = 1.0,
) -> dict[str, float]:
    """
    Calculate annual carbon footprint in tonnes of CO₂e.

    Returns a dict with category-level breakdowns and a total.
    """
    f = CARBON_EMISSION_FACTORS

    # Electricity (monthly kWh → annual kg CO₂e)
    electricity = electricity_kwh_per_month * 12 * f["electricity_india"]

    # LPG (cylinders → kg CO₂e)
    lpg = lpg_cylinders_per_year * f["lpg_cylinder"]

    # Transport (daily km → annual kg CO₂e)
    car_factor = f.get(f"car_{car_fuel_type}", f["car_petrol"])
    transport = (
        car_km_per_day * 365 * car_factor
        + bike_km_per_day * 365 * f["motorbike_petrol"]
        + bus_km_per_day * 365 * f["bus"]
        + metro_km_per_day * 365 * f["metro_rail"]
        + flights_per_year * avg_flight_km * 2 * f["flight_economy"]  # round-trip
    )

    # Diet (annual kg CO₂e)
    diet_key = f"diet_{diet_type}"
    diet = f.get(diet_key, f["diet_medium_meat"]) * 365

    # Food waste (weekly → annual kg CO₂e)
    food_waste = food_waste_kg_per_week * 52 * f["food_waste"]

    total = electricity + lpg + transport + diet + food_waste

    return {
        "electricity_tco2e": round(electricity / 1000, 3),
        "lpg_tco2e": round(lpg / 1000, 3),
        "transport_tco2e": round(transport / 1000, 3),
        "diet_tco2e": round(diet / 1000, 3),
        "food_waste_tco2e": round(food_waste / 1000, 3),
        "total_tco2e": round(total / 1000, 3),
    }


def get_eco_score_label(total_tco2e: float) -> tuple[str, str]:
    """Return (grade, description) for a carbon total."""
    thresholds = ECO_SCORE_THRESHOLDS
    if total_tco2e < thresholds["excellent"]:
        return "A+", "Excellent — your footprint is below the Paris Agreement target!"
    elif total_tco2e < thresholds["good"]:
        return "A", "Good — you are close to a sustainable lifestyle."
    elif total_tco2e < thresholds["average"]:
        return "B", "Average — there is good room for improvement."
    elif total_tco2e < thresholds["needs_work"]:
        return "C", "Needs work — consider the action plan below."
    else:
        return "D", "High footprint — immediate action is recommended."


# ── Text Utilities ───────────────────────────────────────────

def clean_text(text: str) -> str:
    """Normalise whitespace and remove control characters."""
    text = re.sub(r"[\r\n]+", " ", text)
    text = re.sub(r"\s{2,}", " ", text)
    return text.strip()


def truncate_text(text: str, max_chars: int = 300) -> str:
    """Truncate text to max_chars, adding ellipsis if needed."""
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rsplit(" ", 1)[0] + "…"


def hash_text(text: str) -> str:
    """Return a short SHA-256 hash of text (useful for doc IDs)."""
    return hashlib.sha256(text.encode()).hexdigest()[:16]


def format_source_citation(source: str, title: str, prefix: str = "📚 Source") -> str:
    """Format a source citation string."""
    return f"{prefix}: **{title}** — {source}"


# ── Preference Helpers ───────────────────────────────────────

def build_user_context_string(preferences: dict[str, Any]) -> str:
    """
    Build a human-readable context string from user preference dict
    to inject into prompts for personalisation.
    """
    parts = []
    if preferences.get("location"):
        parts.append(f"Location: {preferences['location']}")
    if preferences.get("lifestyle"):
        parts.append(f"Lifestyle: {preferences['lifestyle']}")
    if preferences.get("transport"):
        parts.append(f"Primary transport: {preferences['transport']}")
    if preferences.get("household_type"):
        parts.append(f"Household: {preferences['household_type']}")
    if preferences.get("dietary_preference"):
        parts.append(f"Diet: {preferences['dietary_preference']}")
    if not parts:
        return ""
    return "User profile — " + "; ".join(parts) + "."
