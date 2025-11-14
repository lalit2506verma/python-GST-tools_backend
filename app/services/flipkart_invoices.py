import pandas as pd


def convert_event_type(event_type, sheet_name: str) -> str:
    if sheet_name == "sales_report":

        if event_type == "sale":
            return f"sales_{event_type}"

        elif event_type == "return" or event_type == "cancellation":
            return f"sales_rc"

        else:
            return event_type.replace(" ", "-")

    elif sheet_name == "cashback_report":

        if event_type == "sale":
            return f"cashback_{event_type}"

        elif event_type == "return" or event_type == "cancellation":
            return f"cashback_rc"

        else:
            return event_type.replace(" ", "-")

    else:
        return event_type.replace(" ", "-")