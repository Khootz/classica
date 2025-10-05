"""
Comprehensive M&A Document Extraction Schema
Extracts 30+ fields across financial, operational, and deal-specific categories
"""

# Comprehensive extraction schema for M&A due diligence
COMPREHENSIVE_SCHEMA = {
    "type": "object",
    "properties": {
        # === FINANCIAL METRICS ===
        "Company": {"type": "string", "description": "Legal company name"},
        "Revenue": {"type": "string", "description": "Total revenue or sales"},
        "TotalDebt": {"type": "string", "description": "Total debt obligations"},
        "Equity": {"type": "string", "description": "Total shareholder equity"},
        "CashFlow": {"type": "string", "description": "Operating cash flow"},
        "NetIncome": {"type": "string", "description": "Net profit after tax"},
        "EBITDA": {"type": "string", "description": "Earnings before interest, tax, depreciation, amortization"},
        "OperatingIncome": {"type": "string", "description": "Operating profit"},
        "GrossProfit": {"type": "string", "description": "Revenue minus cost of goods sold"},
        "WorkingCapital": {"type": "string", "description": "Current assets minus current liabilities"},
        "CapEx": {"type": "string", "description": "Capital expenditures"},
        "RevenueGrowthYoY": {"type": "string", "description": "Year-over-year revenue growth percentage"},
        "EBITDAMargin": {"type": "string", "description": "EBITDA as percentage of revenue"},
        "GrossMargin": {"type": "string", "description": "Gross profit as percentage of revenue"},
        
        # === COMPANY INFORMATION ===
        "Industry": {"type": "string", "description": "Primary industry or sector"},
        "Headquarters": {"type": "string", "description": "Location of headquarters"},
        "EmployeeCount": {"type": "string", "description": "Number of employees"},
        "YearFounded": {"type": "string", "description": "Year company was established"},
        "LegalStructure": {"type": "string", "description": "LLC, Corporation, Partnership, etc."},
        "Subsidiaries": {"type": "string", "description": "List of subsidiary companies"},
        
        # === DEAL STRUCTURE ===
        "Valuation": {"type": "string", "description": "Company valuation or purchase price"},
        "EnterpriseValue": {"type": "string", "description": "Total enterprise value"},
        "EquityValue": {"type": "string", "description": "Equity value"},
        "DealType": {"type": "string", "description": "Asset purchase, stock purchase, merger, etc."},
        "PaymentTerms": {"type": "string", "description": "Cash, stock, earnout structure"},
        "EarnoutProvisions": {"type": "string", "description": "Performance-based payment terms"},
        "ClosingConditions": {"type": "string", "description": "Conditions precedent to closing"},
        
        # === RISK FACTORS ===
        "CustomerConcentration": {"type": "string", "description": "Top customer revenue percentage"},
        "SupplierConcentration": {"type": "string", "description": "Key supplier dependencies"},
        "RegulatoryRisks": {"type": "string", "description": "Regulatory compliance issues"},
        "Litigation": {"type": "string", "description": "Pending or threatened lawsuits"},
        "ContingentLiabilities": {"type": "string", "description": "Off-balance sheet liabilities"},
        "MaterialContracts": {"type": "string", "description": "Key customer or supplier agreements"},
        
        # === OPERATIONAL KPIs ===
        "CustomerCount": {"type": "string", "description": "Total number of customers"},
        "CAC": {"type": "string", "description": "Customer acquisition cost"},
        "ChurnRate": {"type": "string", "description": "Customer attrition rate"},
        "LTVtoCACRatio": {"type": "string", "description": "Lifetime value to customer acquisition cost ratio"},
        "MarketShare": {"type": "string", "description": "Market share percentage"}
    },
    "required": []  # Make all optional for flexibility
}

# Categorized field groups for organized display
FIELD_CATEGORIES = {
    "financial_metrics": [
        "Company", "Revenue", "TotalDebt", "Equity", "CashFlow", "NetIncome",
        "EBITDA", "OperatingIncome", "GrossProfit", "WorkingCapital", "CapEx",
        "RevenueGrowthYoY", "EBITDAMargin", "GrossMargin"
    ],
    "company_info": [
        "Industry", "Headquarters", "EmployeeCount", "YearFounded",
        "LegalStructure", "Subsidiaries"
    ],
    "deal_structure": [
        "Valuation", "EnterpriseValue", "EquityValue", "DealType",
        "PaymentTerms", "EarnoutProvisions", "ClosingConditions"
    ],
    "risk_factors": [
        "CustomerConcentration", "SupplierConcentration", "RegulatoryRisks",
        "Litigation", "ContingentLiabilities", "MaterialContracts"
    ],
    "operational_kpis": [
        "CustomerCount", "CAC", "ChurnRate", "LTVtoCACRatio", "MarketShare"
    ]
}

def categorize_extraction(extraction_json: dict) -> dict:
    """Organize extracted fields by category"""
    categorized = {}
    
    for category, fields in FIELD_CATEGORIES.items():
        category_data = {}
        for field in fields:
            if field in extraction_json and extraction_json[field]:
                category_data[field] = extraction_json[field]
        if category_data:
            categorized[category] = category_data
    
    return categorized
