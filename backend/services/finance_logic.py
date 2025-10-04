def safe_float(value):
    """Convert ADE string values like '5,000,000' or '2000000' into float safely."""
    if value is None:
        return None
    try:
        return float(str(value).replace(",", "").replace("$", "").strip())
    except Exception:
        return None

def analyze_financials(extracted_data: dict):
    steps, flags, summary = [], [], []

    rev_23 = safe_float(extracted_data.get("Revenue2023") or extracted_data.get("Revenue"))
    rev_24 = safe_float(extracted_data.get("Revenue2024"))
    if rev_23 and rev_24:
        growth = (rev_24 - rev_23) / rev_23 * 100
        steps.append({"step": "Calculated YoY revenue growth", "value": f"{growth:.2f}%"})
        if growth < 0:
            flags.append("Negative revenue growth 🚩")
        summary.append(f"Revenue growth: {growth:.2f}%")

    debt = safe_float(extracted_data.get("TotalDebt") or extracted_data.get("Debt"))
    equity = safe_float(extracted_data.get("Equity"))
    if debt and equity:
        ratio = debt / equity
        steps.append({"step": "Calculated Debt/Equity ratio", "value": ratio})
        if ratio > 3:
            flags.append("High leverage 🚩")
        summary.append(f"Debt/Equity ratio: {ratio:.2f}")

    cashflow = safe_float(extracted_data.get("CashFlow"))
    if cashflow is not None:
        steps.append({"step": "Captured Cash Flow", "value": cashflow})
        if cashflow < 0:
            flags.append("Negative cash flow 🚩")
        summary.append(f"CashFlow: {cashflow}")

    return {
        "summary": " | ".join(summary) if summary else "No financial metrics extracted",
        "reasoning_log": steps,
        "red_flags": flags
    }
