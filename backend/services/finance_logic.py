from services.pathway_client import process_ade_data

def safe_float(value):
    """Convert ADE string values like '5,000,000' or '$2M' into float safely."""
    if value is None:
        return 0.0
    try:
        return float(str(value).replace(",", "").replace("$", "").strip())
    except Exception:
        return 0.0


def analyze_financials(ade_json):
    """
    CFO agent logic:
    - Uses Pathway’s processed metrics
    - Computes additional ratios and financial insights
    - Always returns a JSON-safe dict with summary + insights
    """
    try:
        results = process_ade_data(ade_json)
    except Exception as e:
        print(f"⚠️ Pathway processing failed: {e}")
        return {"summary": {}, "insights": ["⚠️ Could not process ADE data."]}

    # 🧩 Normalize result type
    metrics = {}
    if isinstance(results, list):
        if results and isinstance(results[0], dict):
            metrics = results[0]
    elif isinstance(results, dict):
        metrics = results

    if not metrics:
        return {"summary": {}, "insights": ["⚠️ No valid financial metrics found."]}

    # ✅ Extract numeric values safely
    revenue = safe_float(metrics.get("revenue") or metrics.get("Revenue"))
    debt = safe_float(metrics.get("debt") or metrics.get("TotalDebt"))
    equity = safe_float(metrics.get("equity") or metrics.get("Equity"))
    cash_flow = safe_float(metrics.get("cash_flow") or metrics.get("CashFlow"))
    net_income = safe_float(metrics.get("net_income") or metrics.get("NetIncome"))
    ebitda = safe_float(metrics.get("ebitda") or metrics.get("EBITDA"))
    op_income = safe_float(metrics.get("operating_income") or metrics.get("OperatingIncome"))

    # ✅ Check if all financial data is zero/missing
    if all(val == 0 for val in [revenue, debt, equity, cash_flow, net_income]):
        return {
            "summary": {},
            "insights": []  # Return empty insights to avoid rendering zero-value metrics
        }

    # ✅ Compute ratios
    debt_to_equity = (debt / equity) if equity else 0
    debt_to_revenue = (debt / revenue) if revenue else 0
    net_margin = (net_income / revenue) if revenue else 0
    roe = (net_income / equity) if equity else 0
    cashflow_to_debt = (cash_flow / debt) if debt else 0

    # 🧾 Build summary
    summary = {
        "revenue": revenue,
        "debt": debt,
        "equity": equity,
        "cash_flow": cash_flow,
        "net_income": net_income,
        "ebitda": ebitda,
        "operating_income": op_income,
        "debt_to_equity": round(debt_to_equity, 2),
        "debt_to_revenue": round(debt_to_revenue, 2),
        "net_margin": round(net_margin, 2),
        "return_on_equity": round(roe, 2),
        "cashflow_to_debt": round(cashflow_to_debt, 2),
    }

    # 🧠 Generate insights
    insights = []

    # Leverage
    if debt_to_equity > 2:
        insights.append(f"⚠️ High leverage: debt-to-equity ratio {debt_to_equity:.2f}")
    elif 1.0 < debt_to_equity <= 2:
        insights.append(f"⚠️ Moderate leverage: debt-to-equity ratio {debt_to_equity:.2f}")
    else:
        insights.append(f"✅ Healthy leverage: debt-to-equity ratio {debt_to_equity:.2f}")

    # Liquidity
    if debt_to_revenue > 1:
        insights.append(f"⚠️ Debt exceeds annual revenue ({debt_to_revenue:.2f}) — possible liquidity pressure.")
    else:
        insights.append(f"✅ Revenue comfortably covers debt ({debt_to_revenue:.2f}×).")

    # Profitability
    if net_margin > 0.25:
        insights.append(f"💰 Strong profitability: net margin {net_margin*100:.1f}%")
    elif net_margin > 0.1:
        insights.append(f"🙂 Moderate profitability: net margin {net_margin*100:.1f}%")
    else:
        insights.append(f"⚠️ Low profitability: net margin {net_margin*100:.1f}%")

    # Efficiency
    if roe > 0.15:
        insights.append(f"💼 Strong return on equity ({roe*100:.1f}%) — efficient capital use.")
    elif roe > 0.05:
        insights.append(f"⚙️ Acceptable return on equity ({roe*100:.1f}%).")
    else:
        insights.append(f"⚠️ Weak return on equity ({roe*100:.1f}%).")

    # Cash Flow
    if cashflow_to_debt < 0.1:
        insights.append(f"⚠️ Weak debt coverage by cash flow ({cashflow_to_debt*100:.1f}%).")
    else:
        insights.append(f"✅ Cash flow sufficiently covers debt ({cashflow_to_debt*100:.1f}%).")

    # Summary if no red flags
    if not insights:
        insights.append("✅ All financial indicators appear strong.")

    return {"summary": summary, "insights": insights}
