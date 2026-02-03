import streamlit as st
import google.generativeai as genai
import numpy_financial as npf

GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
model = genai.GenerativeModel('gemini-1.5-pro-latest')

# App Styling
st.set_page_config(page_title="WealthPreneurs DealFlow", layout="wide")
st.title("🏢 WealthPreneurs DealFlow Automator")
st.markdown("### Deal Finder Submission Portal")

# --- SIDEBAR: ASSUMPTIONS ---
with st.sidebar:
    st.header("Loan & Market Assumptions")
    st.info("Adjust these for DSCR/IRR calculations")
    down_payment_pct = st.slider("Down Payment %", 10, 50, 25) / 100
    interest_rate = st.number_input("Interest Rate %", value=7.5) / 100
    loan_term_years = st.number_input("Loan Term (Years)", value=30)
    holding_period = 5 # for IRR calc

# --- STEP 1: INPUTS ---
col1, col2, col3 = st.columns(3)

with col1:
    address = st.text_input("Property Address")
    zip_code = st.text_input("Zip Code")
    sqft = st.number_input("Square Footage", min_value=0)

with col2:
    purchase_price = st.number_input("Purchase Price ($)", min_value=0.0, format="%.2f")
    capex_budget = st.number_input("Est. CapEx/Rehab ($)", min_value=0.0, format="%.2f")

with col3:
    gross_monthly_rent = st.number_input("Gross Monthly Rent ($)", min_value=0.0, format="%.2f")
    monthly_expenses = st.number_input("Monthly Expenses (Taxes, Ins, Maint) ($)", min_value=0.0, format="%.2f")

# --- STEP 2: FINANCIAL LOGIC (Hard Math) ---
def calculate_metrics():
    if purchase_price == 0 or gross_monthly_rent == 0:
        return None

    # Income & Expense
    annual_gross_income = gross_monthly_rent * 12
    annual_expenses = monthly_expenses * 12
    noi = annual_gross_income - annual_expenses
    
    # Loan Calc
    loan_amount = purchase_price * (1 - down_payment_pct)
    monthly_rate = interest_rate / 12
    num_payments = loan_term_years * 12
    # Standard mortgage payment formula
    monthly_debt_service = loan_amount * (monthly_rate * (1 + monthly_rate) ** num_payments) / ((1 + monthly_rate) ** num_payments - 1) 
    annual_debt_service = monthly_debt_service * 12
    
    # Metrics
    cash_flow = noi - annual_debt_service
    total_cash_invested = (purchase_price * down_payment_pct) + capex_budget
    
    coc = (cash_flow / total_cash_invested) * 100
    dscr = noi / annual_debt_service if annual_debt_service > 0 else 0
    multiplier = purchase_price / annual_gross_income if annual_gross_income > 0 else 0
    
    # Simple IRR Approximation (5 Year Hold, 3% appreciation, exit at Cap Rate)
    exit_price = purchase_price * (1.03 ** holding_period)
    cash_flows = [-total_cash_invested] + [cash_flow] * (holding_period - 1) + [cash_flow + (exit_price - (loan_amount * 0.9))] # Rough equity capture
    irr = npf.irr(cash_flows) * 100

    return {
        "NOI": noi,
        "CoC": coc,
        "DSCR": dscr,
        "GRM": multiplier,
        "IRR": irr,
        "Total Cash In": total_cash_invested
    }

metrics = calculate_metrics()

# --- STEP 3: GEMINI AI INTEGRATION ---
if st.button("Analyze Deal & Generate Gamma Deck"):
    if metrics:
        with st.spinner('Crunching numbers and drafting pitch deck...'):
            
            # Formatting prompt for Gemini
            prompt = f"""
            Act as an expert Real Estate Analyst for WealthPreneurs Capital.
            I have a deal at {address}, {zip_code}.
            
            Financials:
            - Purchase Price: ${purchase_price}
            - NOI: ${metrics['NOI']}
            - CapEx: ${capex_budget}
            - DSCR: {metrics['DSCR']:.2f}
            - CoC Return: {metrics['CoC']:.2f}%
            
            Task 1: Verify the address context. Briefly describe the neighborhood vibe (schools, crime, growth) based on the Zip Code {zip_code}.
            Task 2: Suggest a deal structure (e.g., creative finance, bridge debt, or standard value-add) based on the DSCR and CapEx.
            Task 3: Define 2 Exit Strategies (e.g., BRRRR, Flip, or Buy & Hold).
            
            Task 4: Create a 'Gamma Paste' Outline. This must be formatted specifically so I can paste it into Gamma.app to auto-generate slides. 
            Use 'Card' or 'Slide' headers. Include a 'One Page Teaser' section at the start.
            """
            
            response = model.generate_content(prompt)
            
            # --- DISPLAY DASHBOARD ---
            st.divider()
            
            # Top Row Metrics
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("NOI (Annual)", f"${metrics['NOI']:,.0f}")
            m2.metric("DSCR", f"{metrics['DSCR']:.2f}", delta_color="normal" if metrics['DSCR'] > 1.25 else "inverse")
            m3.metric("Cash on Cash", f"{metrics['CoC']:.1f}%")
            m4.metric("IRR (5yr proj)", f"{metrics['IRR']:.1f}%")

            # AI Analysis Section
            st.subheader("🤖 AI Deal Analysis")
            st.write(response.text)

            # Raw Data for Copying
            st.text_area("Copy this for Gamma (Ctrl+C)", value=response.text, height=300)
            
    else:
        st.error("Please fill in Price and Rent to calculate.")


