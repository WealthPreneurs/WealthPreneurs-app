import streamlit as st
import google.generativeai as genai
import numpy_financial as npf
import requests  # <--- NEW IMPORT

# --- CONFIGURATION ---
try:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
    # We use .get() here so the app doesn't crash if you haven't added the key yet
    GAMMA_API_KEY = st.secrets.get("GAMMA_API_KEY", None) 
except FileNotFoundError:
    st.error("Secrets file not found. Please create .streamlit/secrets.toml")
    st.stop()

genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-pro-latest')

# ... [KEEP ALL PREVIOUS INPUTS AND CALCULATION LOGIC THE SAME] ...

# --- STEP 3: GEMINI & GAMMA INTEGRATION ---
if st.button("Analyze Deal & Generate Deck"):
    if metrics:
        with st.spinner('Crunching numbers and drafting deck...'):
            
            # 1. Generate Content with Gemini
            prompt = f"""
            [Insert the detailed prompt from the previous response here]
            """
            response = model.generate_content(prompt)
            generated_text = response.text

            # --- OPTION A: AUTOMATIC API TRIGGER (If Key Exists) ---
            if GAMMA_API_KEY:
                st.info("Gamma API Key detected. Attempting to send to Gamma...")
                
                try:
                    # REPLACE THIS URL with the actual endpoint from your Gamma docs
                    # Example: https://api.gamma.app/v1/generate (Hypothetical)
                    gamma_endpoint = "https://api.gamma.app/marketing/generate-deck" 
                    
                    headers = {
                        "Authorization": f"Bearer {GAMMA_API_KEY}",
                        "Content-Type": "application/json"
                    }
                    
                    payload = {
                        "prompt": generated_text,
                        "mode": "presentation"
                    }
                    
                    api_response = requests.post(gamma_endpoint, json=payload, headers=headers)
                    
                    if api_response.status_code == 200:
                        st.success("🎉 Sent to Gamma successfully! Check your dashboard.")
                        st.json(api_response.json())
                    else:
                        st.error(f"Gamma API Error: {api_response.status_code}")
                        st.write(api_response.text)
                        
                except Exception as e:
                    st.error(f"Connection failed: {e}")
            
            # --- OPTION B: MANUAL FALLBACK (Always Safe) ---
            st.divider()
            st.subheader("📋 Manual Integration (Backup)")
            st.text_area("Copy this text for Gamma 'Paste to Create':", value=generated_text, height=300)
            
    else:
        st.error("Please ensure Price and Rent are filled in.")

