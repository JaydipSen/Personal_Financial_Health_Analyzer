import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Personal Financial Health Analyzer",
    page_icon="💰",
    layout="wide"
)

st.title("💰 Personal Financial Health Analyzer")
st.markdown("""
An interactive dashboard to evaluate your personal financial condition,
monthly cash flow, spending habits, debt, savings, investments, and financial goals.
""")

# ==================== SIDEBAR INPUTS ====================

st.sidebar.header("Financial Information")

currency = st.sidebar.selectbox(
    "Currency", ["₹", "$", "€", "£"], index=0
)

st.sidebar.subheader("Personal Profile")
age = st.sidebar.number_input("Age", 18, 100, 30)
dependents = st.sidebar.number_input("Number of dependents", 0, 20, 0)

st.sidebar.subheader("Monthly Income")
salary = st.sidebar.number_input("Monthly salary", min_value=0.0, value=80000.0)
other_income = st.sidebar.number_input("Other monthly income", min_value=0.0, value=10000.0)
income = salary + other_income

st.sidebar.subheader("Monthly Expenses")
expense_defaults = {
    "Housing": 18000,
    "Food": 10000,
    "Transport": 5000,
    "Utilities": 3000,
    "Healthcare": 2000,
    "Education": 3000,
    "Shopping": 6000,
    "Entertainment": 2500,
    "Insurance": 2500,
    "Other": 3000
}

expenses = {}
for category, default in expense_defaults.items():
    expenses[category] = st.sidebar.number_input(
        category, min_value=0.0, value=float(default), step=500.0
    )

living_expenses = sum(expenses.values())

st.sidebar.subheader("Loans and Debt")
home_loan = st.sidebar.number_input("Home loan outstanding", min_value=0.0, value=0.0)
personal_loan = st.sidebar.number_input("Personal loan outstanding", min_value=0.0, value=150000.0)
vehicle_loan = st.sidebar.number_input("Vehicle loan outstanding", min_value=0.0, value=0.0)
credit_card = st.sidebar.number_input("Credit card outstanding", min_value=0.0, value=25000.0)
emi = st.sidebar.number_input("Monthly EMI payments", min_value=0.0, value=12000.0)

st.sidebar.subheader("Assets and Investments")
bank_cash = st.sidebar.number_input("Bank balance / cash", min_value=0.0, value=100000.0)
emergency_fund = st.sidebar.number_input("Emergency fund", min_value=0.0, value=80000.0)
fixed_deposits = st.sidebar.number_input("Fixed deposits", min_value=0.0, value=100000.0)
mutual_funds = st.sidebar.number_input("Mutual funds", min_value=0.0, value=200000.0)
stocks = st.sidebar.number_input("Stocks / ETFs", min_value=0.0, value=100000.0)
retirement = st.sidebar.number_input("Retirement / provident fund", min_value=0.0, value=150000.0)
real_estate = st.sidebar.number_input("Real estate value", min_value=0.0, value=0.0)
other_assets = st.sidebar.number_input("Other assets", min_value=0.0, value=0.0)

st.sidebar.subheader("Financial Goals")
savings_target = st.sidebar.number_input("Desired monthly savings", min_value=0.0, value=15000.0)
emergency_months_target = st.sidebar.slider("Emergency fund target (months)", 3, 12, 6)
monthly_investment = st.sidebar.number_input("Planned monthly investment", min_value=0.0, value=10000.0)
annual_return = st.sidebar.slider("Expected annual investment return (%)", 0.0, 15.0, 7.0)
projection_years = st.sidebar.slider("Investment projection (years)", 1, 30, 10)

# ==================== CALCULATIONS ====================

monthly_outflow = living_expenses + emi
surplus = income - monthly_outflow

savings_rate = surplus / income * 100 if income else 0
expense_ratio = living_expenses / income * 100 if income else 0
debt_ratio = emi / income * 100 if income else 0

total_debt = home_loan + personal_loan + vehicle_loan + credit_card

assets = {
    "Cash": bank_cash,
    "Fixed Deposits": fixed_deposits,
    "Mutual Funds": mutual_funds,
    "Stocks": stocks,
    "Retirement": retirement,
    "Real Estate": real_estate,
    "Other Assets": other_assets
}

total_assets = sum(assets.values())
net_worth = total_assets - total_debt
debt_asset_ratio = total_debt / total_assets * 100 if total_assets else 0
emergency_coverage = emergency_fund / living_expenses if living_expenses else 0
emergency_target = living_expenses * emergency_months_target
emergency_gap = max(0, emergency_target - emergency_fund)

# Illustrative health score
score_savings = min(max(savings_rate / 20 * 100, 0), 100)
score_debt = min(max(100 - debt_ratio / 40 * 100, 0), 100)
score_emergency = min(emergency_coverage / emergency_months_target * 100, 100)
score_networth = 100 if net_worth > 0 else 30
score_expenses = min(max(100 - expense_ratio / 90 * 100, 0), 100)

health_score = round(
    score_savings * 0.25
    + score_debt * 0.20
    + score_emergency * 0.25
    + score_networth * 0.15
    + score_expenses * 0.15
)

if health_score >= 80:
    health_status = "Strong"
elif health_score >= 60:
    health_status = "Moderate"
elif health_score >= 40:
    health_status = "Needs Improvement"
else:
    health_status = "At Risk"

# ==================== OVERVIEW ====================

st.header("1. Financial Overview")

c1, c2, c3, c4, c5 = st.columns(5)

c1.metric("Monthly Income", f"{currency}{income:,.0f}")
c2.metric("Monthly Expenses", f"{currency}{living_expenses:,.0f}")
c3.metric("Monthly Surplus", f"{currency}{surplus:,.0f}")
c4.metric("Net Worth", f"{currency}{net_worth:,.0f}")
c5.metric("Health Score", f"{health_score}/100", health_status)

# Health score gauge
gauge = go.Figure(go.Indicator(
    mode="gauge+number",
    value=health_score,
    title={"text": "Financial Health Score"},
    gauge={
        "axis": {"range": [0, 100]},
        "steps": [
            {"range": [0, 40]},
            {"range": [40, 60]},
            {"range": [60, 80]},
            {"range": [80, 100]}
        ]
    }
))
gauge.update_layout(height=300)
st.plotly_chart(gauge, use_container_width=True)

if surplus < 0:
    st.error(f"Monthly deficit: {currency}{abs(surplus):,.0f}")
else:
    st.success(f"Monthly surplus: {currency}{surplus:,.0f}")

# ==================== CASH FLOW ====================

st.header("2. Cash Flow Analysis")

waterfall = go.Figure(go.Waterfall(
    x=["Income", "Living Expenses", "EMI", "Surplus"],
    y=[income, -living_expenses, -emi, 0],
    measure=["absolute", "relative", "relative", "total"]
))
waterfall.update_layout(title="Income-to-Surplus Waterfall", height=400)
st.plotly_chart(waterfall, use_container_width=True)

# Income allocation
allocation = pd.DataFrame({
    "Category": ["Living Expenses", "EMI", "Surplus"],
    "Amount": [living_expenses, emi, max(surplus, 0)]
})
allocation = allocation[allocation["Amount"] > 0]

fig = px.pie(
    allocation, names="Category", values="Amount",
    hole=0.4, title="Monthly Income Allocation"
)
st.plotly_chart(fig, use_container_width=True)

# ==================== EXPENSE ANALYSIS ====================

st.header("3. Expense Analysis")

expense_df = pd.DataFrame({
    "Category": list(expenses.keys()),
    "Amount": list(expenses.values())
}).sort_values("Amount", ascending=False)

fig = px.bar(
    expense_df, x="Category", y="Amount",
    title="Monthly Expense Category Comparison",
    text_auto=".2s"
)
st.plotly_chart(fig, use_container_width=True)

fig = px.pie(
    expense_df, names="Category", values="Amount",
    hole=0.45, title="Expense Distribution"
)
st.plotly_chart(fig, use_container_width=True)

fig = px.treemap(
    expense_df, path=["Category"], values="Amount",
    title="Expense Treemap"
)
st.plotly_chart(fig, use_container_width=True)

# Pareto chart
pareto = expense_df.sort_values("Amount", ascending=False).copy()
pareto["Cumulative Percentage"] = (
    pareto["Amount"].cumsum() / pareto["Amount"].sum() * 100
)

fig = go.Figure()
fig.add_trace(go.Bar(
    x=pareto["Category"], y=pareto["Amount"], name="Expense"
))
fig.add_trace(go.Scatter(
    x=pareto["Category"],
    y=pareto["Cumulative Percentage"],
    name="Cumulative %",
    yaxis="y2", mode="lines+markers"
))
fig.update_layout(
    title="Expense Pareto Analysis",
    yaxis2=dict(overlaying="y", side="right", range=[0, 100]),
    height=400
)
st.plotly_chart(fig, use_container_width=True)

# ==================== FINANCIAL RATIOS ====================

st.header("4. Financial Ratios")

r1, r2, r3 = st.columns(3)
r1.metric("Expense / Income", f"{expense_ratio:.1f}%")
r2.metric("Savings Rate", f"{savings_rate:.1f}%")
r3.metric("EMI / Income", f"{debt_ratio:.1f}%")

ratio_df = pd.DataFrame({
    "Ratio": ["Expense Ratio", "Savings Rate", "Debt Repayment Ratio"],
    "Current": [expense_ratio, savings_rate, debt_ratio],
    "Illustrative Benchmark": [50, 20, 30]
})

ratio_chart = px.bar(
    ratio_df, x="Ratio", y=["Current", "Illustrative Benchmark"],
    barmode="group", title="Current Ratios vs Illustrative Benchmarks"
)
st.plotly_chart(ratio_chart, use_container_width=True)

# ==================== SAVINGS ANALYSIS ====================

st.header("5. Savings Analysis")

st.metric("Monthly Savings", f"{currency}{surplus:,.0f}")
st.metric("Savings Target", f"{currency}{savings_target:,.0f}")

savings_progress = min(max(surplus / savings_target, 0), 1) if savings_target else 0
st.progress(savings_progress)
st.caption(f"Target achievement: {savings_progress * 100:.1f}%")

savings_gauge = go.Figure(go.Indicator(
    mode="gauge+number",
    value=max(0, savings_rate),
    number={"suffix": "%"},
    title={"text": "Savings Rate"},
    gauge={"axis": {"range": [0, 100]}}
))
savings_gauge.update_layout(height=300)
st.plotly_chart(savings_gauge, use_container_width=True)

# ==================== EMERGENCY FUND ====================

st.header("6. Emergency Fund Analysis")

e1, e2, e3 = st.columns(3)
e1.metric("Current Emergency Fund", f"{currency}{emergency_fund:,.0f}")
e2.metric("Coverage", f"{emergency_coverage:.1f} months")
e3.metric("Target Gap", f"{currency}{emergency_gap:,.0f}")

emergency_fig = go.Figure(go.Indicator(
    mode="gauge+number",
    value=min(emergency_coverage, emergency_months_target),
    number={"suffix": " months"},
    title={"text": "Emergency Fund Coverage"},
    gauge={"axis": {"range": [0, emergency_months_target]}}
))
emergency_fig.update_layout(height=300)
st.plotly_chart(emergency_fig, use_container_width=True)

# ==================== DEBT ANALYSIS ====================

st.header("7. Debt Analysis")

debt_items = {
    "Home Loan": home_loan,
    "Personal Loan": personal_loan,
    "Vehicle Loan": vehicle_loan,
    "Credit Card": credit_card
}

debt_df = pd.DataFrame({
    "Debt Type": list(debt_items.keys()),
    "Outstanding": list(debt_items.values())
})

d1, d2, d3 = st.columns(3)
d1.metric("Total Debt", f"{currency}{total_debt:,.0f}")
d2.metric("Debt / Asset Ratio", f"{debt_asset_ratio:.1f}%")
d3.metric("Monthly EMI", f"{currency}{emi:,.0f}")

debt_nonzero = debt_df[debt_df["Outstanding"] > 0]

if not debt_nonzero.empty:
    fig = px.pie(
        debt_nonzero, names="Debt Type", values="Outstanding",
        hole=0.4, title="Debt Composition"
    )
    st.plotly_chart(fig, use_container_width=True)

fig = px.bar(
    debt_df, x="Debt Type", y="Outstanding",
    title="Outstanding Debt by Category"
)
st.plotly_chart(fig, use_container_width=True)

# ==================== ASSET ANALYSIS ====================

st.header("8. Asset Allocation")

asset_df = pd.DataFrame({
    "Asset": list(assets.keys()),
    "Value": list(assets.values())
})
asset_nonzero = asset_df[asset_df["Value"] > 0]

fig = px.pie(
    asset_nonzero, names="Asset", values="Value",
    hole=0.4, title="Asset Allocation"
)
st.plotly_chart(fig, use_container_width=True)

fig = px.bar(
    asset_df, x="Asset", y="Value",
    title="Asset Value Comparison"
)
st.plotly_chart(fig, use_container_width=True)

fig = px.treemap(
    asset_nonzero, path=["Asset"], values="Value",
    title="Asset Allocation Treemap"
)
st.plotly_chart(fig, use_container_width=True)

# ==================== NET WORTH ====================

st.header("9. Net Worth Analysis")

balance_sheet = pd.DataFrame({
    "Type": ["Assets", "Liabilities", "Net Worth"],
    "Amount": [total_assets, total_debt, net_worth]
})

fig = px.bar(
    balance_sheet, x="Type", y="Amount",
    title="Personal Balance Sheet"
)
st.plotly_chart(fig, use_container_width=True)

# ==================== INVESTMENT PROJECTION ====================

st.header("10. Investment Projection")

monthly_rate = (1 + annual_return / 100) ** (1 / 12) - 1

projection = []
balance = 0

for month in range(1, projection_years * 12 + 1):
    balance = balance * (1 + monthly_rate) + monthly_investment

    if month % 12 == 0:
        contributed = monthly_investment * month
        projection.append({
            "Year": month // 12,
            "Portfolio Value": balance,
            "Contributions": contributed,
            "Growth": balance - contributed
        })

projection_df = pd.DataFrame(projection)

fig = px.bar(
    projection_df, x="Year",
    y=["Contributions", "Growth"],
    title="Investment Growth Projection",
    barmode="stack"
)
st.plotly_chart(fig, use_container_width=True)

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=projection_df["Year"], y=projection_df["Portfolio Value"],
    name="Portfolio Value", mode="lines+markers"
))
fig.add_trace(go.Scatter(
    x=projection_df["Year"], y=projection_df["Contributions"],
    name="Contributions", mode="lines+markers"
))
fig.update_layout(title="Investment Value vs Contributions")
st.plotly_chart(fig, use_container_width=True)

st.metric(
    "Projected Value",
    f"{currency}{projection_df['Portfolio Value'].iloc[-1]:,.0f}"
)

# ==================== WHAT-IF ANALYSIS ====================

st.header("11. What-If Scenario Analysis")

income_change = st.slider("Income Change (%)", -30, 50, 0, 5)
expense_change = st.slider("Expense Change (%)", -30, 50, 0, 5)

scenario_income = income * (1 + income_change / 100)
scenario_expenses = living_expenses * (1 + expense_change / 100)
scenario_surplus = scenario_income - scenario_expenses - emi

scenario_df = pd.DataFrame({
    "Scenario": ["Current", "What-if"],
    "Income": [income, scenario_income],
    "Expenses + EMI": [monthly_outflow, scenario_expenses + emi],
    "Surplus": [surplus, scenario_surplus]
})

fig = px.bar(
    scenario_df, x="Scenario",
    y=["Income", "Expenses + EMI", "Surplus"],
    barmode="group", title="Scenario Comparison"
)
st.plotly_chart(fig, use_container_width=True)

st.metric("What-if Surplus", f"{currency}{scenario_surplus:,.0f}")

# ==================== SUMMARY ====================

st.header("12. Financial Recommendations")

recommendations = []

if surplus < 0:
    recommendations.append("Your expenses exceed your income. Review discretionary spending and recurring commitments.")
if savings_rate < 10:
    recommendations.append("Consider building a consistent savings habit and gradually increasing your savings rate.")
if emergency_coverage < emergency_months_target:
    recommendations.append("Build your emergency fund toward your selected coverage target.")
if debt_ratio > 35:
    recommendations.append("Your EMI burden is relatively high compared with income. Review debt obligations.")
if net_worth < 0:
    recommendations.append("Your liabilities exceed your assets. Track net worth and consider a sustainable debt-reduction plan.")
if savings_rate >= 20:
    recommendations.append("Your savings rate meets or exceeds the illustrative 20% benchmark.")

if not recommendations:
    recommendations.append("Continue monitoring your cash flow, savings, debt, and net worth.")

for recommendation in recommendations:
    st.write("🔹", recommendation)

# ==================== DOWNLOAD ====================

st.header("13. Download Your Financial Summary")

summary = pd.DataFrame({
    "Metric": [
        "Monthly Income", "Living Expenses", "EMI",
        "Monthly Surplus", "Savings Rate (%)",
        "Emergency Fund Coverage (Months)",
        "Total Assets", "Total Debt", "Net Worth",
        "Financial Health Score"
    ],
    "Value": [
        income, living_expenses, emi, surplus, savings_rate,
        emergency_coverage, total_assets, total_debt, net_worth,
        health_score
    ]
})

st.download_button(
    "Download Summary CSV",
    summary.to_csv(index=False),
    "financial_health_summary.csv",
    "text/csv"
)

st.download_button(
    "Download Expense Details CSV",
    expense_df.to_csv(index=False),
    "expense_breakdown.csv",
    "text/csv"
)

st.info("""
**Educational disclaimer:** This dashboard is designed for financial-literacy
workshops. It is not financial, investment, tax, or legal advice.
Investment projections assume a constant return and do not account for
inflation, fees, taxes, or market fluctuations.
""")