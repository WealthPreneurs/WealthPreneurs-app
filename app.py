import streamlit as st
import google.generativeai as genai
import numpy_financial as npf

# --- 1. SECURE API SETUP ---
try:
    # Ensure this matches the name in your Streamlit Advanced Settings
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
    
    # STEP A: Configure the library (This line returns nothing)
    genai.configure(api_key=GOOGLE_API_KEY)
    
    # STEP B: Initialize the model separately (Solves AttributeError)
    model = genai.GenerativeModel('gemini-1.5-pro-latest')
except Exception as e:
    st.error(f"Configuration Error: {e}")
    st.stop()

# --- 2. INPUT FIELDS ---
# (Keep your existing price, rent, and address inputs here)
purchase_price = st.number_input("Purchase Price ($)", min_value=0.0)
gross_monthly_rent = st.number_input("Gross Monthly Rent ($)", min_value=0.0)

# --- 3. THE CALCULATION ENGINE ---
def calculate_metrics():
    # This prevents the 'NoneType' math errors
    if purchase_price <= 0 or gross_monthly_rent <= 0:
        return None
    
    # ... (Your math logic for NOI, CoC, etc.) ...
    noi = (gross_monthly_rent * 12) * 0.65 # Example simplified math
    return {"NOI": noi}

# CRITICAL FIX: Define metrics BEFORE the button so it is 'defined'
metrics = calculate_metrics()

# --- 4. THE ACTION BUTTON ---
if st.button("Analyze Deal & Generate Deck"):
    if metrics:
        with st.spinner('AI is generating your analysis...'):
            prompt = f"Analyze this deal with an NOI of ${metrics['NOI']}"
            
            # This will now work because 'model' is properly initialized
            response = model.generate_content(prompt)
            st.write(response.text)
    else:
        # This handles the pink warning shown in your image
        st.warning("Please enter a Purchase Price and Monthly Rent to calculate.")

