import pathway as pw


# 🧩 Define a schema that matches normalized ADE data
class AdeSchema(pw.Schema):
    company: str
    revenue: float
    debt: float
    equity: float
    cash_flow: float
    net_income: float
    ebitda: float
    operating_income: float


def process_ade_data(ade_json):
    """
    Converts ADE JSON (single or list) into a Pathway table,
    computes key financial metrics, and returns clean JSON-safe results.
    Handles variations in field names and ensures schema correctness.
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

    # 2️⃣ Ensure all required keys exist
    for key in [
        "company", "revenue", "debt", "equity",
        "cash_flow", "net_income", "ebitda", "operating_income"
    ]:
        normalized.setdefault(key, 0)

    # 3️⃣ Build table from rows using AdeSchema
    ade_table = pw.debug.table_from_rows(
        rows=[(
            normalized["company"],
            float(str(normalized["revenue"]).replace(",", "").replace("$", "") or 0),
            float(str(normalized["debt"]).replace(",", "").replace("$", "") or 0),
            float(str(normalized["equity"]).replace(",", "").replace("$", "") or 0),
            float(str(normalized["cash_flow"]).replace(",", "").replace("$", "") or 0),
            float(str(normalized["net_income"]).replace(",", "").replace("$", "") or 0),
            float(str(normalized["ebitda"]).replace(",", "").replace("$", "") or 0),
            float(str(normalized["operating_income"]).replace(",", "").replace("$", "") or 0),
        )],
        schema=AdeSchema
    )

    # 4️⃣ Compute derived metrics
    processed = ade_table.select(
        company=pw.this.company,
        revenue=pw.this.revenue,
        debt=pw.this.debt,
        equity=pw.this.equity,
        cash_flow=pw.this.cash_flow,
        net_income=pw.this.net_income,
        ebitda=pw.this.ebitda,
        operating_income=pw.this.operating_income,
        debt_to_equity=pw.coalesce(pw.this.debt / pw.this.equity, 0.0),
        debt_to_revenue=pw.coalesce(pw.this.debt / pw.this.revenue, 0.0),
        net_margin=pw.coalesce(pw.this.net_income / pw.this.revenue, 0.0),
        return_on_equity=pw.coalesce(pw.this.net_income / pw.this.equity, 0.0),
        cashflow_to_debt=pw.coalesce(pw.this.cash_flow / pw.this.debt, 0.0),
    )

    # 5️⃣ Convert to list of dicts (materialize Pathway output)
    raw_result = list(pw.debug.table_to_dicts(processed))

    # 6️⃣ Flatten if nested list and clean materialized output
    flattened = []
    for row in raw_result:
        if isinstance(row, list):  # e.g., [[{...}]]
            flattened.extend(row)
        else:
            flattened.append(row)

    clean_result = []
    for row in flattened:
        if not isinstance(row, dict):
            continue
        clean_row = {}
        for k, v in row.items():
            try:
                # Convert lazy Pathway pointers or complex objects to floats/strings
                if hasattr(v, "value") or "pathway.engine" in str(type(v)):
                    clean_row[k] = float(str(v))
                elif isinstance(v, (float, int)):
                    clean_row[k] = v
                else:
                    val_str = str(v).replace(",", "").replace("$", "").strip()
                    clean_row[k] = float(val_str) if val_str.replace('.', '', 1).isdigit() else val_str
            except Exception:
                clean_row[k] = str(v)
        clean_result.append(clean_row)

    print("✅ Pathway processed ADE data (flattened + cleaned):", clean_result)
    return clean_result
