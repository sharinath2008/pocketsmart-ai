"""
Wraps Google's Gemini (model set via GEMINI_MODEL) for all three planners.

Handles:
  - Text-only prompts (Home Planner, Party Planner)
  - Multimodal text+image prompts (Jewelry Planner, outfit photo upload)
  - Per-planner prompt templates tuned for budget interpretation
  - A safe fallback response if Gemini errors or returns something unusable
"""
import google.generativeai as genai
from PIL import Image

from config import Config

if Config.GEMINI_API_KEY:
    genai.configure(api_key=Config.GEMINI_API_KEY)

_model = genai.GenerativeModel(Config.GEMINI_MODEL) if Config.GEMINI_API_KEY else None


PROMPT_TEMPLATES = {
    "home": (
        "You are a home interior planning assistant. A user has a budget of "
        "{budget} and wants to furnish: {details}. "
        "Recommend a practical set of items that fit the budget, with a rough "
        "price for each and a one-line reason for the pick. Keep it concise."
    ),
    "party": (
        "You are a party planning assistant. Event type: {event_type}. "
        "Budget: {budget}. Number of guests: {guests}. "
        "Suggest a realistic plan covering venue/decor, food, and entertainment "
        "that fits the budget, with approximate costs per category."
    ),
    "jewelry": (
        "You are a jewelry styling assistant. Budget: {budget}. Occasion: "
        "{occasion}. If an outfit image is provided, consider its color and "
        "style. Recommend 2-3 jewelry pieces that complement the outfit and "
        "occasion within budget, with approximate prices."
    ),
}

FALLBACK_RESPONSES = {
    "home": "We couldn't generate a custom plan right now. A safe default: "
            "prioritize seating and lighting first, then decor, within your budget.",
    "party": "We couldn't generate a custom plan right now. A safe default: "
             "allocate roughly 50% to food, 30% to venue/decor, 20% to extras.",
    "jewelry": "We couldn't generate a custom plan right now. A safe default: "
               "a simple pendant necklace and stud earrings suit most occasions.",
}


class GeminiError(Exception):
    pass


def _build_prompt(planner: str, fields: dict) -> str:
    template = PROMPT_TEMPLATES.get(planner)
    if not template:
        raise GeminiError(f"Unknown planner type: {planner}")
    try:
        return template.format(**fields)
    except KeyError as exc:
        raise GeminiError(f"Missing field for prompt: {exc}")


def generate_recommendation(planner: str, fields: dict, image_path: str | None = None) -> str:
    """
    Calls Gemini with a planner-specific prompt, optionally attaching an
    image for multimodal input (used by the Jewelry Planner). Falls back
    to a canned response on any failure so the API never returns nothing.
    """
    if _model is None:
        return FALLBACK_RESPONSES.get(planner, "AI service is not configured.")

    prompt = _build_prompt(planner, fields)

    try:
        if image_path:
            image = Image.open(image_path)
            response = _model.generate_content([prompt, image])
        else:
            response = _model.generate_content(prompt)

        text = (response.text or "").strip()
        if not text:
            raise GeminiError("Empty response from Gemini")
        return text

    except Exception:
        # Any failure (rate limit, bad image, network error, etc.) —
        # degrade gracefully instead of surfacing a 500 to the user.
        return FALLBACK_RESPONSES.get(planner, "Something went wrong generating your plan.")
