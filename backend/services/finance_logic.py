def analyze_financials(extracted_data: dict):
    steps, flags, summary = [], [], []

    rev_23 = extracted_data.get("Revenue2023")
    rev_24 = extracted_data.get("Revenue2024")
    if rev_23 and rev_24:
        growth = (rev_24 - rev_23) / rev_23 * 100
        steps.append({"step": "Calculated YoY revenue growth", "value": f"{growth:.2f}%"})
        if growth < 0:
            flags.append("Negative revenue growth 🚩")
        summary.append(f"Revenue growth: {growth:.2f}%")

    debt = extracted_data.get("TotalDebt")
    equity = extracted_data.get("Equity")
    if debt and equity:
        ratio = debt / equity
        steps.append({"step": "Calculated Debt/Equity ratio", "value": ratio})
        if ratio > 3:
            flags.append("High leverage 🚩")
        summary.append(f"Debt/Equity ratio: {ratio:.2f}")

    return {
        "summary": " | ".join(summary),
        "reasoning_log": steps,
        "red_flags": flags
    }
