"""
SpendWise Dashboard – Simple Streamlit frontend for demo & screenshots.
Run: streamlit run dashboard.py
"""

import streamlit as st
import requests
from datetime import datetime, timedelta
import pandas as pd

API_URL = st.sidebar.text_input("API URL", "http://localhost:8000")

st.set_page_config(page_title="SpendWise", page_icon="💰", layout="wide")
st.title("💰 SpendWise – Personal Finance Analytics")

# ---------- Auth State ----------
if "token" not in st.session_state:
    st.session_state.token = None
if "user" not in st.session_state:
    st.session_state.user = None


def api_headers():
    return {"Authorization": f"Bearer {st.session_state.token}"} if st.session_state.token else {}


# ---------- Login / Register ----------
if not st.session_state.token:
    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login"):
            res = requests.post(
                f"{API_URL}/api/auth/login",
                data={"username": email, "password": password},
            )
            if res.status_code == 200:
                st.session_state.token = res.json()["access_token"]
                st.success("Logged in!")
                st.rerun()
            else:
                st.error(res.json().get("detail", "Login failed"))

    with tab2:
        full_name = st.text_input("Full Name")
        reg_email = st.text_input("Email", key="reg_email")
        reg_pass = st.text_input("Password", type="password", key="reg_pass")
        if st.button("Create Account"):
            res = requests.post(
                f"{API_URL}/api/auth/register",
                json={"email": reg_email, "full_name": full_name, "password": reg_pass},
            )
            if res.status_code == 201:
                st.success("Account created! Please login.")
            else:
                st.error(res.json().get("detail", "Registration failed"))

else:
    # ---------- Main Dashboard ----------
    col1, col2 = st.columns([4, 1])
    with col2:
        if st.button("Logout"):
            st.session_state.token = None
            st.rerun()

    # Summary
    st.subheader("📊 Overview")
    summary = requests.get(f"{API_URL}/api/analytics/summary", headers=api_headers()).json()

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Income", f"₹{summary['total_income']:,.0f}")
    m2.metric("Total Expense", f"₹{summary['total_expense']:,.0f}")
    m3.metric("Net Savings", f"₹{summary['net_savings']:,.0f}")
    m4.metric("Savings Rate", f"{summary['savings_rate']}%")

    # Category breakdown
    st.subheader("🏷️ Spending by Category")
    cats = requests.get(
        f"{API_URL}/api/analytics/by-category",
        headers=api_headers(),
        params={"type": "expense"},
    ).json()

    if cats:
        df_cat = pd.DataFrame(cats)
        st.bar_chart(df_cat.set_index("category_name")["total_amount"])
        st.dataframe(df_cat[["category_name", "total_amount", "percentage", "transaction_count"]], hide_index=True)
    else:
        st.info("No expense data yet. Add transactions!")

    # Monthly trend
    st.subheader("📈 Monthly Trend")
    trend = requests.get(
        f"{API_URL}/api/analytics/monthly-trend",
        headers=api_headers(),
        params={"months": 6},
    ).json()

    if trend:
        df_trend = pd.DataFrame(trend)
        df_trend["month_label"] = df_trend.apply(lambda r: f"{int(r['year'])}-{int(r['month']):02d}", axis=1)
        st.line_chart(df_trend.set_index("month_label")[["income", "expense", "net"]])
    else:
        st.info("Not enough data for trends.")

    # Recent transactions
    st.subheader("🧾 Recent Transactions")
    txs = requests.get(
        f"{API_URL}/api/transactions/",
        headers=api_headers(),
        params={"limit": 20},
    ).json()

    if txs:
        df_tx = pd.DataFrame(txs)
        st.dataframe(
            df_tx[["transaction_date", "type", "amount", "description"]],
            hide_index=True,
        )
    else:
        st.info("No transactions yet.")

    # Quick add
    with st.expander("➕ Add Transaction"):
        amount = st.number_input("Amount", min_value=0.01, step=10.0)
        tx_type = st.selectbox("Type", ["expense", "income"])
        description = st.text_input("Description")
        if st.button("Save"):
            res = requests.post(
                f"{API_URL}/api/transactions/",
                headers=api_headers(),
                json={
                    "amount": amount,
                    "type": tx_type,
                    "description": description,
                },
            )
            if res.status_code == 201:
                st.success("Transaction added!")
                st.rerun()
            else:
                st.error("Failed to add transaction")
