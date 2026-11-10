import os
from datetime import datetime

import streamlit as st
from google import genai
from google.genai import types

st.set_page_config(page_title="ScentSense Perfume Analyzer", page_icon="🌸", layout="wide")

MODEL_NAME = "gemini-2.5-flash"

st.markdown("""
<style>
.stApp {background: linear-gradient(135deg, #fffaf7, #f7eff4, #fff8ef);}
.hero {background: linear-gradient(120deg,#382437,#75485f,#bd8580); color:white;
       padding:32px; border-radius:22px; margin-bottom:20px;}
.hero h1 {font-size:42px; margin:0;}
.hero p {color:#f8eaf0;}
div[data-testid="stForm"] {background:rgba(255,255,255,.8); padding:20px;
                           border:1px solid #eadde5; border-radius:18px;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
  <h1>🌸 ScentSense</h1>
  <p>AI-Powered Perfume Analyzer and Fragrance Recommendations</p>
</div>
""", unsafe_allow_html=True)


def get_api_key():
    try:
        key = st.secrets.get("GEMINI_API_KEY", "")
    except Exception:
        key = ""
    return key or os.getenv("GEMINI_API_KEY", "")


def build_prompt(perfume_name, brand, category, occasion, season, budget, currency):
    name = perfume_name.strip() or "Not provided"
    brand_name = brand.strip() or "Not provided"
    budget_text = str(budget) + " " + currency if budget > 0 else "Not specified"

    parts = [
        "You are a careful perfume expert. Analyze using reliable knowledge only.",
        "Perfume name: " + name,
        "Brand: " + brand_name,
        "Preferred fragrance category: " + category,
        "Occasion: " + occasion,
        "Season: " + season,
        "Budget: " + budget_text,
        "",
        "Do not invent perfume identity, notes, longevity, projection, sillage, or prices.",
        "If information is uncertain, say Not reliably known.",
        "Do not claim to have checked live prices or official databases.",
        "Clearly label performance as AI estimates, not measured specifications.",
        "Recommendations must be real perfumes you are confident exist.",
        "The rating is an AI opinion, not an objective or customer-review score.",
        "",
        "# Perfume Analysis",
        "## 1. Identification",
        "## 2. Fragrance Profile",
        "## 3. Fragrance Notes",
        "Top notes, middle notes, and base notes.",
        "## 4. Longevity",
        "## 5. Projection and Sillage",
        "## 6. Occasion Recommendations",
        "## 7. Season Recommendations",
        "## 8. Similar Perfume Recommendations",
        "Suggest up to three, and tell the user to check local prices.",
        "## 9. Fragrance Personality",
        "## 10. Overall AI Rating",
        "Give a score out of 10 with an explanation.",
        "## 11. Reliability and Limitations",
        "Separate user-provided details, model knowledge, estimates, and unknowns."
    ]
    return "\n".join(parts)


def analyze_perfume(api_key, prompt, image_file=None):
    client = genai.Client(api_key=api_key)
    contents = [prompt]

    if image_file is not None:
        image_bytes = image_file.getvalue()
        mime_type = image_file.type or "image/jpeg"
        image_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
        contents.append(image_part)

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=contents,
        config=types.GenerateContentConfig(
            temperature=0.25,
            max_output_tokens=2500
