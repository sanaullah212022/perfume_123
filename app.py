import re
from datetime import datetime

import streamlit as st
from google import genai
from google.genai import types

# ---------------------------------------------------------
# App configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="ScentSense | AI Perfume Analyzer",
    page_icon="🌸",
    layout="wide",
    initial_sidebar_state="expanded",
)

DEFAULT_MODEL = "gemini-2.5-flash"

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@600;700&display=swap');
    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
    .stApp { background: linear-gradient(135deg, #fffaf7 0%, #f7f0f5 52%, #fdf8f0 100%); }
    .hero {
        padding: 2.2rem 2.4rem; border-radius: 24px; color: white;
        background: linear-gradient(115deg, #3d2638 0%, #70465d 55%, #b77b79 100%);
        margin-bottom: 1.4rem; box-shadow: 0 12px 35px rgba(61,38,56,.15);
    }
    .hero h1 { font-family: 'Playfair Display', serif; font-size: 2.5rem; margin: 0; }
    .hero p { color: #f8eaf0; margin: .45rem 0 0; font-size: 1.02rem; }
    .eyebrow { text-transform: uppercase; letter-spacing: .18em; font-size: .72rem; color: #f4cbd8; font-weight: 700; }
    .note { background: #fff; border: 1px solid #eadde5; padding: 1rem 1.1rem; border-radius: 14px; }
    div[data-testid="stForm"] { background: rgba(255,255,255,.72); padding: 1.2rem; border: 1px solid #eadde5; border-radius: 18px; }
    .stButton>button, .stDownloadButton>button { border-radius: 12px; font-weight: 700; }
    h2, h3 { font-family: 'Playfair Display', serif !important; color: #4a2e43; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------
def get_api_settings():
    """Read the API key from Streamlit Secrets or environment variables."""
    api_key = None
    model = DEFAULT_MODEL

    try:
        api_key = st.secrets.get("GEMINI_API_KEY", None)
        model = st.secrets.get("GEMINI_MODEL", DEFAULT_MODEL)
    except Exception:
        # st.secrets may not exist during first-time local setup.
        pass

    if not api_key:
        import os
        api_key = os.getenv("GEMINI_API_KEY")

    if not model:
        model = DEFAULT_MODEL

    return api_key, model


def clean_markdown(text):
    """Remove accidental outer Markdown code fences from model output."""
    text = (text or "").strip()
    text = re.sub(r"^```(?:markdown|md|text)?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()


def build_prompt(perfume_name, brand, category, occasion, season, budget, currency):
    name = perfume_name.strip() or "Not provided"
    brand_name = brand.strip() or "Not provided"
    budget_text = f"{budget:,.0f} {currency}" if budget and budget > 0 else "Not specified"

    return f"""
You are a careful perfume educator and fragrance recommendation assistant.
Analyze the perfume using your reliable existing knowledge and the user's input.
Do not claim to have checked a live database, retailer, official brand page, or current price.

USER INPUT
- Perfume name: {name}
- Brand: {brand_name}
- Preferred fragrance family: {category}
- Occasion: {occasion}
- Preferred season: {season}
- Budget: {budget_text}

IMPORTANT ACCURACY RULES
1. Never invent perfume identity, scent notes, concentration, longevity, projection, sillage, release year, or price.
2. If you cannot confidently identify the perfume, say "Unable to identify confidently" and ask for clearer label details. Do not guess from a vague bottle image.
