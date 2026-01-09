## app.py
import streamlit as st
import requests
from urllib.parse import quote

st.set_page_config(page_title="AI Image Generator", page_icon="🎨", layout="centered")

st.title("AI Image Generator")
st.caption("Powered by Pollinations AI")

# --- UI controls ---
prompt = st.text_input("Enter your prompt:", value="A fantasy castle on a floating island")
col1, col2, col3 = st.columns(3)
with col1:
    model = st.selectbox("Model", ["flux", "sd3", "sdxl", "stable-diffusion"], index=0)
with col2:
    aspect = st.selectbox("Aspect ratio", ["square", "portrait", "landscape"], index=0)
with col3:
    seed = st.number_input("Seed (optional)", min_value=0, value=0, step=1)

generate = st.button("Generate image")

# --- helpers ---
def build_pollinations_url(prompt: str, model: str, aspect: str, seed: int) -> str:
    base = "https://image.pollinations.ai/prompt/"
    encoded_prompt = quote(prompt.strip())
    params = []

    # Model
    if model:
        params.append(f"model={model}")

    # Aspect ratio mapping
    if aspect == "square":
        params.append("width=768&height=768")
    elif aspect == "portrait":
        params.append("width=640&height=896")
    elif aspect == "landscape":
        params.append("width=896&height=640")

    # Seed (0 means let API choose)
    if seed and seed > 0:
        params.append(f"seed={seed}")

    query = "&".join(params)
    return f"{base}{encoded_prompt}" + (f"?{query}" if query else "")

@st.cache_data(show_spinner=False)
def fetch_image_bytes(url: str) -> bytes:
    # shorter timeout so user doesn’t wait forever
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    return resp.content

# --- generation flow ---
if generate:
    if not prompt.strip():
        st.error("Please enter a prompt.")
    else:
        with st.spinner("Generating your image... please wait ⏳"):
            try:
                url = build_pollinations_url(prompt, model, aspect, seed)
                img_bytes = fetch_image_bytes(url)
                st.success("Image generated successfully! 🎉")
                st.image(img_bytes, caption=prompt, use_column_width=True)

                # Optional: show the URL for reproducibility
                with st.expander("Image URL"):
                    st.code(url)

            except requests.HTTPError as e:
                st.error(f"Generation failed: {e.response.status_code} {e.response.reason}")
                if st.button("Retry"):
                    st.experimental_rerun()

            except requests.RequestException:
                st.error("⚠️ Network error or timeout. Try again with a simpler prompt or click Retry.")
                if st.button("Retry"):
                    st.experimental_rerun()
                    
