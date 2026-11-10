import os
from datetime import datetime

import streamlit as st
from google import genai
from google.genai import types

st.set_page_config(page_title="ScentSense - Perfume Analyzer", page_icon="🌸", layout="wide")
MODEL_NAME = "gemini-2.5-flash"

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@600;700&display=swap');
.stApp {background:linear-gradient(135deg,#fffaf7,#f7eff4,#fff8ef);}
html,body,[class*="css"] {font-family:'DM Sans',sans-serif;}
.hero {background:linear-gradient(120deg,#382437,#75485f,#bd8580);color:white;padding:34px;border-radius:22px;margin-bottom:22px;}
.hero h1 {font-family:'Playfair Display',serif;font-size:42px;margin:5px 0;}
.hero p {color:#f8eaf0;margin:0;}
div[data-testid="stForm"] {background:rgba(255,255,255,.8);padding:22px;border:1px solid #eadde5;border-radius:18px;}
h2,h3 {color:#56364c;font-family:'Playfair Display',serif;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
  <div style="letter-spacing:3px;font-size:12px;">DISCOVER YOUR SIGNATURE SCENT</div>
  <h1>🌸 ScentSense</h1>
  <p>AI-Powered Perfume Analyzer & Personal Fragrance Recommendations</p>
</div>
""", unsafe_allow_html=True)
st.write("Enter perfume details, upload a bottle photo, and choose your preferences.")


def get_api_key():
    """Read the key from Streamlit Secrets or the environment."""
    try:
        key = st.secrets.get("GEMINI_API_KEY", "")
    except Exception:
        key = ""
    return key or os.getenv("GEMINI_API_KEY", "")


def build_prompt(perfume_name, brand, category, occasion, season, budget, currency):
    """Build the prompt with normal strings to avoid multiline quote errors."""
    name = perfume_name.strip() or "Not provided"
    brand_name = brand.strip() or "Not provided"
    budget_text = (str(budget) + " " + currency) if budget > 0 else "Not specified"

    prompt_lines = [
        "You are a careful perfume educator and fragrance recommendation assistant.",
        "Analyze the perfume using reliable knowledge and the user's input.",
        "Do not claim to have checked a live database or current retailer prices.",
        "",
        "USER INPUT:",
        "Perfume name: " + name,
        "Brand: " + brand_name,
        "Preferred fragrance category: " + category,
        "Occasion: " + occasion,
        "Preferred season: " + season,
        "Budget: " + budget_text,
        "",
        "ACCURACY RULES:",
        "1. Never invent perfume identity, scent notes, longevity, projection, sillage, or prices.",
        "2. If identity is uncertain, say 'Unable to identify confidently'. Do not guess from a vague image.",
        "3. Separate user-provided information, model knowledge, and AI estimates.",
        "4. If notes are uncertain, say 'Not reliably known'.",
        "5. Longevity and projection vary by skin, climate, application, and formulation.",
        "6. Label performance statements as estimates, not measured specifications.",
        "7. Recommend only real perfumes you are reasonably confident exist.",
        "8. Do not claim current prices or availability; ask the user to check local retailers.",
        "9. The rating is an AI opinion, not an objective or customer-review score.",
        "",
        "Write a clear report using these headings:",
        "# Perfume Analysis",
        "## 1. Identification",
        "## 2. Fragrance Profile",
        "## 3. Fragrance Notes (top, middle, and base)",
        "## 4. Longevity",
        "## 5. Projection and Sillage",
        "## 6. Occasion Recommendations",
        "## 7. Season Recommendations",
        "## 8. Similar Perfume Recommendations (up to 3)",
        "## 9. Fragrance Personality",
        "## 10. Overall AI Rating (out of 10, with explanation)",
        "## 11. Reliability and Limitations",
        "At the end, separate supplied information, model knowledge, AI estimates, and unknown details.",
        "Do not fill missing information with guesses."
    ]
    return "\n".join(prompt_lines)


def analyze_perfume(api_key, prompt, image_file=None):
    client = genai.Client(api_key=api_key)
    contents = [prompt]
    if image_file is not None:
        image_part = types.Part.from_bytes(
