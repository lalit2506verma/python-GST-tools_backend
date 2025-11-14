import pandas as pd
from app.utils.invoice_numbers import min_max_whole

DOC_TYPE_MAPPING = {
    "INVOICE": "Invoices for outward supply",
    "sales_sale": "Invoices for outward supply",
    "CREDIT NOTE": "Credit Note",
    "sales_rc": "Credit Note",
    "cashback_sale": "Credit Note",
    "cashback_rc": "Debit Note",
    "return-cancellation": "Debit Note",
    # extend later:
    # "DEBIT NOTE": "Debit Note",
    # "REVISED INVOICE": "Revised Invoice",
    # "INWARD UNREG": "Invoices for inward supply from unregistered person",
}

def generate_invoice_summary(df: pd.DataFrame, doc_type: str, col: str) -> pd.DataFrame:
    nature = DOC_TYPE_MAPPING.get(doc_type)
    if not nature:
        raise ValueError(f"Unsupported doc_type: {doc_type}")

    # print(df)
    min_inv, max_inv, count = min_max_whole(df, col)
    cancelled = 0  # hook later if you add a status column

    return pd.DataFrame([{
        "Nature of Document": nature,
        "Sr. No. From": min_inv,
        "Sr. No. To": max_inv,
        "Total Number": count,
        "Cancelled": cancelled
    }])
