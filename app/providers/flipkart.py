import pandas as pd
from typing_extensions import override

from app.providers.base import SalesProvider


class FlipkartProvider(SalesProvider):
    name = "flipkart"

    @staticmethod
    def _derive_gst_rate(row: pd.Series) -> int:
        """
        Flipkart provides IGST, SGST, CGST separately.
        - If IGST > 0 → gst_rate = IGST
        - Else → gst_rate = SGST + CGST
        """
        igst = float(row.get("IGST Rate", 0.0))
        cgst = float(row.get("CGST Rate", 0.0))
        sgst = float(row.get("SGST Rate (or UTGST as applicable)", 0.0))

        if igst > 0.0:
            return int(round(igst))
        return int(round(cgst + sgst))

    @override
    def normalize_sales(self, sales_df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalizes Flipkart file into standard schema.
        File already contains both sales and returns,
        returns come as negative taxable values.
        """

        required_cols = {
            "Taxable Value (Final Invoice Amount -Taxes)",
            "Customer's Delivery State",
            "IGST Rate",
            "CGST Rate",
            "SGST Rate (or UTGST as applicable)",
        }
        missing = required_cols - set(sales_df.columns)
        if missing:
            raise ValueError(f"Missing required columns in Flipkart file: {missing}")

        df = sales_df.copy()
        print("dataframe copied")

        # derive gst rate per row
        df["gst_rate"] = df.apply(self._derive_gst_rate, axis=1)
        print("gst_rate applied")

        # rename columns to standard schema
        df.rename(
            columns={
                "Taxable Value (Final Invoice Amount -Taxes)": "total_taxable_sale_value",
                "Customer's Delivery State": "end_customer_state_new",
            },
            inplace=True,
        )

        print("Column name changed")
        print(df)

        return df[["end_customer_state_new", "total_taxable_sale_value", "gst_rate"]]

    @override
    def normalize_returns(self, cashback_df: pd.DataFrame) -> pd.DataFrame:

        required_cols = {
            "Taxable Value",
            "Customer's Delivery State",
            "IGST Rate",
            "CGST Rate",
            "SGST Rate (or UTGST as applicable)",
        }

        missing = required_cols - set(cashback_df.columns)
        if missing:
            raise ValueError(f"Missing required columns in Flipkart file: {missing}")

        df = cashback_df.copy()
        print("dataframe copied")

        # derive gst rate per row
        df["gst_rate"] = df.apply(self._derive_gst_rate, axis=1)
        print("gst_rate applied")

        # rename columns to standard schema
        df.rename(
            columns={
                "Taxable Value": "total_taxable_sale_value",
                "Customer's Delivery State": "end_customer_state_new",
            },
            inplace=True,
        )

        print("Column name changed")
        print(df)

        return df[["end_customer_state_new", "total_taxable_sale_value", "gst_rate"]]
