# Mock version for Windows - Pathway doesn't support Windows natively
# This provides the same functionality without Pathway dependencies

def safe_float(value):
    """Convert a value to float safely"""
    if value is None or value == "":
        return 0.0
    try:
        return float(str(value).replace(",", "").replace("$", "").strip())
    except:
        return 0.0

def safe_divide(a, b):
    """Safely divide two numbers, return 0 if division by zero"""
    try:
        if b == 0 or b is None:
            return 0.0
        return float(a) / float(b)
    except:
        return 0.0

def process_ade_data(ade_json):
    """
    Converts ADE JSON (single or list) and computes key financial metrics.
    Handles variations in field names and ensures schema correctness.
    Windows-compatible version without Pathway.
    """
    if not ade_json:
        print("⚠️ Empty ADE JSON provided.")
        return []

    # 🧠 If ADE JSON is a list (e.g., multiple docs merged), flatten & merge
    if isinstance(ade_json, list):
        merged = {}
        for entry in ade_json:
            if isinstance(entry, dict):
                for k, v in entry.items():
                    merged[k] = v
        ade_json = merged

    # 1️⃣ Normalize all keys (case + aliases)
    normalized = {}
    for k, v in ade_json.items():
        key = k.lower().strip()
        if key in ["totaldebt", "debt"]:
            key = "debt"
        elif key in ["cashflow", "cash_flow"]:
            key = "cash_flow"
        elif key in ["netincome", "net_income"]:
            key = "net_income"
        elif key in ["operatingincome", "operating_income"]:
            key = "operating_income"
        elif key in ["companyname", "name"]:
            key = "company"
        normalized[key] = v

    # 2️⃣ Ensure all required keys exist and convert to floats
    company = normalized.get("company", "Unknown")
    revenue = safe_float(normalized.get("revenue", 0))
    debt = safe_float(normalized.get("debt", 0))
    equity = safe_float(normalized.get("equity", 0))
    cash_flow = safe_float(normalized.get("cash_flow", 0))
    net_income = safe_float(normalized.get("net_income", 0))
    ebitda = safe_float(normalized.get("ebitda", 0))
    operating_income = safe_float(normalized.get("operating_income", 0))

    # 3️⃣ Compute derived metrics
    result = {
        "company": company,
        "revenue": revenue,
        "debt": debt,
        "equity": equity,
        "cash_flow": cash_flow,
        "net_income": net_income,
        "ebitda": ebitda,
        "operating_income": operating_income,
        "debt_to_equity": safe_divide(debt, equity),
        "debt_to_revenue": safe_divide(debt, revenue),
        "net_margin": safe_divide(net_income, revenue),
        "return_on_equity": safe_divide(net_income, equity),
        "cashflow_to_debt": safe_divide(cash_flow, debt),
    }

    clean_result = [result]
    print("✅ Processed ADE data (Windows-compatible):", clean_result)
    return clean_result
