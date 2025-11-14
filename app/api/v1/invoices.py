from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
import pandas as pd, tempfile
from app.services.fileio import read_file
from app.services.flipkart_invoices import convert_event_type
from app.services.invoices import generate_invoice_summary

router = APIRouter(tags=["Invoices"])

flipkart_custom_doc_type = [
    "sales_sale",
    "sales_rc",
    "cashback_sale",
    "cashback_rc",
    "return-cancellation"
]

@router.post("/meesho-tax_invoice/")
async def m_tax_invoice(tax_invoice: UploadFile = File(...)):
    df = read_file(tax_invoice, 0)
    required = ["Type", "Invoice No."]
    if not all(c in df.columns for c in required):
        raise HTTPException(status_code=422, detail=f"Missing required columns: {required}")

    out_rows = []
    for key in ["INVOICE", "CREDIT NOTE"]:
        part = df[df["Type"] == key].copy()
        out_rows.append(generate_invoice_summary(part, key, col="Invoice No."))

    summary = pd.concat(out_rows, ignore_index=True)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
        summary.to_csv(tmp.name, index=False)
        return FileResponse(tmp.name, filename="invoice_summary.csv", media_type="text/csv")

# GET COMBINED DATAFRAME OF SALES AND CASHBACK
def flipkart_tax_invoice(sales_df: pd.DataFrame, cashback_df: pd.DataFrame):

    """
        Before combining the sales and cashback dataframes
        modify the EVENT_TYPE column so that invoice stats can be extracted
        Ex: Sale(sale_report) -> sale_sale and Return(cashback) -> cashback_return
    """

    sales_df["event_type"] = sales_df["event_type"].apply(
        lambda x: convert_event_type(x.lower(), "sales_report")
    )
    cashback_df["event_type"] = cashback_df["event_type"].apply(
        lambda x: convert_event_type(x.lower(), "cashback_report")
    )

    required = ["event_type", "invoice_number"]

    df = pd.concat([sales_df[required], cashback_df[required]])
    print(df)
    out_rows = []
    for key in flipkart_custom_doc_type:
        part = df[df["event_type"] == key].copy()
        print(part)
        out_rows.append(generate_invoice_summary(part, key, col="invoice_number"))

    summary = pd.concat(out_rows, ignore_index=True)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
        summary.to_csv(tmp.name, index=False)
        return FileResponse(tmp.name, filename="flipkart_docs.csv", media_type="text/csv")

