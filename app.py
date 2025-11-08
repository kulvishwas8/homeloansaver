import streamlit as st
import pandas as pd
import math

# Page configuration
st.set_page_config(
    page_title="Home Loan Saver",
    page_icon="",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
.main-header {
    font-size: 2.5rem;
    font-weight: bold;
    color: #1f77b4;
    text-align: center;
    margin-bottom: 2rem;
}
.section-header {
    font-size: 1.5rem;
    font-weight: bold;
    color: #2c3e50;
    margin-top: 2rem;
    margin-bottom: 1rem;
    border-bottom: 2px solid #1f77b4;
    padding-bottom: 0.5rem;
}
.metric-card {
    background-color: #f0f2f6;
    padding: 1.5rem;
    border-radius: 10px;
    border-left: 5px solid #1f77b4;
    margin-bottom: 1rem;
}
.savings-card {
    background-color: #d4edda;
    padding: 1.5rem;
    border-radius: 10px;
    border-left: 5px solid #28a745;
    margin-top: 2rem;
}
.no-savings-card {
    background-color: #f8d7da;
    padding: 1.5rem;
    border-radius: 10px;
    border-left: 5px solid #dc3545;
    margin-top: 2rem;
}
</style>
""", unsafe_allow_html=True)

# Title
st.markdown('<div class="main-header">Home Loan Saver</div>',
            unsafe_allow_html=True)

# Info section
with st.expander("What is an OD Home Loan?", expanded=False):
    st.markdown("""
**Understanding OD (Overdraft) Home Loan:**

In a normal home loan, you borrow a fixed amount and pay interest on the entire principal every month.

An OD Home Loan links your loan to a savings account. Any money parked there:
- Reduces the principal amount on which interest is calculated
- Remains accessible for emergencies
- Saves interest effectively

Example: ₹1 Crore loan with ₹10 Lakhs in OD account = Interest charged only on ₹90 Lakhs
""")

st.markdown("---")

# User Inputs
st.markdown('<div class="section-header"> Enter Your Details</div>',
            unsafe_allow_html=True)
col1, col2 = st.columns(2)

with col1:
    monthly_pay = st.number_input(
        " Net Take-Home Monthly Pay (₹)", 10000, 10000000, 100000, 1000)
    loan_amount = st.number_input(
        " Home Loan Amount (₹)", 100000, 100000000, 5000000, 1000)
    tenure_years = st.number_input(" Loan Tenure (Years)", 1, 30, 20, 1)

with col2:
    normal_rate = st.number_input(
        " Normal Home Loan Interest Rate (%)", 1.0, 20.0, 8.5, 0.05)
    od_rate = st.number_input(
        " OD Home Loan Interest Rate (%)", 1.0, 20.0, 8.5, 0.05)

    min_od_amount = int(monthly_pay * 2)
    max_od_amount = int(loan_amount)
    default_od_value = min(max(min_od_amount, 0), max_od_amount)

    od_amount = st.number_input(" Amount to Keep in OD Account (₹)",
                                min_od_amount, max_od_amount, default_od_value, 1000)

if od_amount < min_od_amount:
    st.error(f" OD amount must be at least ₹{min_od_amount:,.0f}")
    st.stop()
if od_amount > loan_amount:
    st.error(f" OD amount cannot exceed the loan amount ₹{loan_amount:,.0f}")
    st.stop()

st.markdown("---")

# EMI Calculations


def calculate_emi(principal, annual_rate, tenure_months):
    monthly_rate = annual_rate / (12 * 100)
    if monthly_rate == 0:
        return principal / tenure_months
    emi = principal * monthly_rate * \
        math.pow(1 + monthly_rate, tenure_months) / \
        (math.pow(1 + monthly_rate, tenure_months) - 1)
    return emi


def calculate_normal_loan(principal, annual_rate, tenure_years):
    tenure_months = tenure_years * 12
    emi = calculate_emi(principal, annual_rate, tenure_months)
    total_payment = emi * tenure_months
    total_interest = total_payment - principal
    return {'emi': emi, 'num_emis': tenure_months, 'total_payment': total_payment, 'total_interest': total_interest}


def calculate_od_loan(principal, annual_rate, tenure_years, od_amount, monthly_income):
    monthly_rate = annual_rate / (12 * 100)
    tenure_months = tenure_years * 12
    normal_emi = calculate_emi(principal, annual_rate, tenure_months)
    outstanding = principal
    total_interest = 0.0
    months_taken = 0
    od_balance = od_amount
    monthly_surplus = monthly_income * 0.3

    for month in range(1, tenure_months + 1):
        if outstanding <= 0:
            break
        effective_principal = max(outstanding - od_balance, 0)
        monthly_interest = effective_principal * monthly_rate
        total_interest += monthly_interest
        principal_payment = normal_emi - monthly_interest
        outstanding -= principal_payment
        if od_balance < principal and outstanding > 0:
            od_balance = min(od_balance + monthly_surplus, outstanding)
        months_taken = month
    return {'emi': normal_emi, 'num_emis': months_taken, 'total_payment': normal_emi * months_taken, 'total_interest': total_interest}


with st.spinner(" Calculating your loan options..."):
    normal_loan = calculate_normal_loan(loan_amount, normal_rate, tenure_years)
    od_loan = calculate_od_loan(
        loan_amount, od_rate, tenure_years, od_amount, monthly_pay)

st.markdown('<div class="section-header"> Loan Comparison Results</div>',
            unsafe_allow_html=True)
colA, colB = st.columns(2)

with colA:
    st.markdown("###  Normal Home Loan")
    st.metric("Monthly EMI", f"₹{normal_loan['emi']:,.2f}")
    st.metric("Number of EMIs", f"{normal_loan['num_emis']} months")
    st.metric("Total Interest Outgo", f"₹{normal_loan['total_interest']:,.2f}")
    st.metric("Total Payment", f"₹{normal_loan['total_payment']:,.2f}")

with colB:
    st.markdown("###  OD Home Loan")
    st.metric("Monthly EMI", f"₹{od_loan['emi']:,.2f}")
    st.metric("Number of EMIs", f"{od_loan['num_emis']} months")
    st.metric("Total Interest Outgo", f"₹{od_loan['total_interest']:,.2f}")
    st.metric("Total Payment", f"₹{od_loan['total_payment']:,.2f}")

# Savings Analysis
st.markdown('<div class="section-header"> Savings Analysis</div>',
            unsafe_allow_html=True)
emi_savings = normal_loan['num_emis'] - od_loan['num_emis']
interest_savings = normal_loan['total_interest'] - od_loan['total_interest']
total_savings = normal_loan['total_payment'] - od_loan['total_payment']

if interest_savings > 0 and emi_savings > 0:
    st.success(
        f" You save ₹{total_savings:,.2f} | {emi_savings} EMIs earlier | Interest saved ₹{interest_savings:,.2f}")
else:
    st.error(" No significant savings found with OD Home Loan.")

# Detailed Breakdown
with st.expander("📋 Detailed Breakdown", expanded=False):
    comparison_df = pd.DataFrame({
        'Parameter': [
            'Loan Amount', 'Monthly EMI', 'Number of EMIs', 'Total Payment', 'Total Interest',
            'OD Amount Used', 'Effective Principal (Avg)'
        ],
        'Normal Home Loan': [
            f"₹{loan_amount:,.0f}", f"₹{normal_loan['emi']:,.2f}", f"{normal_loan['num_emis']} months",
            f"₹{normal_loan['total_payment']:,.2f}", f"₹{normal_loan['total_interest']:,.2f}", "N/A",
            f"₹{loan_amount:,.0f}"
        ],
        'OD Home Loan': [
            f"₹{loan_amount:,.0f}", f"₹{od_loan['emi']:,.2f}", f"{od_loan['num_emis']} months",
            f"₹{od_loan['total_payment']:,.2f}", f"₹{od_loan['total_interest']:,.2f}",
            f"₹{od_amount:,.0f}", f"₹{loan_amount - od_amount:,.0f}"
        ]
    })
    st.dataframe(comparison_df, use_container_width=True)


def load_visitor_count():
    try:
        with open("visitor_count.txt", "r") as f:
            count = int(f.read().strip())
    except FileNotFoundError:
        count = 0
    return count


def increment_visitor_count():
    count = load_visitor_count() + 1
    with open("visitor_count.txt", "w") as f:
        f.write(str(count))
    return count


visitor_count = increment_visitor_count()
st.markdown(f"   Visitor Count:   {visitor_count}")

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #7f8c8d; padding: 2rem;">
<p><strong>Disclaimer:</strong> This calculator provides estimates based on simplified assumptions. Consult your bank for accurate figures and other details.</p>
<p>Made by Vishwas Kulkarni (kulvishwas8) for smart financial planning</p>
</div>
""", unsafe_allow_html=True)

