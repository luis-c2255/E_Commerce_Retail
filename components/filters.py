import panel as pn
import pandas as pd

def global_filters(df):

    countries = sorted(df["Country"].dropna().unique())
    customers = sorted(df["CustomerID"].dropna().unique())

    # Country filter (default = all)
    country_filter = pn.widgets.MultiChoice(
        name="Country",
        options=countries,
        value=countries,
        sizing_mode="stretch_width",
    )

    # Date range filter
    start_date = pd.to_datetime(df["InvoiceDate"].min())
    end_date = pd.to_datetime(df["InvoiceDate"].max())

    date_range = pn.widgets.DateRangeSlider(
        name="Invoice Date",
        start=start_date,
        end=end_date,
        value=(start_date, end_date),
        sizing_mode="stretch_width",
    )

    # Customer filter (autocomplete for performance)
    customer_filter = pn.widgets.AutocompleteInput(
        name="CustomerID",
        options=customers,
        placeholder="Type to search customer…",
        case_sensitive=False,
        min_characters=1,
        sizing_mode="stretch_width",
    )

    return country_filter, date_range, customer_filter
