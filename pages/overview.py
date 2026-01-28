import io
import panel as pn
import hvplot.pandas  # noqa
import pandas as pd

from components.kpi_cards import kpi
from components.utils import load_clean_data
from components.skeleton import skeleton_card

pn.extension()

retail, month_metrics, product_metrics, country_metrics, rfm = load_clean_data()

def view(country_filter, date_range, customer_filter):

    @pn.depends(country_filter, date_range, customer_filter)
    def filtered_retail():
        d = retail.copy()

        if country_filter.value:
            d = d[d["Country"].isin(country_filter.value)]

        if customer_filter.value:
            d = d[d["CustomerID"].isin(customer_filter.value)]

        start, end = date_range.value
        d = d[(d["InvoiceDate"] >= start) & (d["InvoiceDate"] <= end)]

        return d

    @pn.depends(filtered_retail)
    def kpi_row(d: pd.DataFrame):
        if d.empty:
            return pn.Row("No data for current filters.")

        total_revenue = d["TotalAmount"].sum()
        total_orders = d["InvoiceNo"].nunique()
        total_customers = d["CustomerID"].nunique()
        avg_order_value = total_revenue / total_orders if total_orders else 0

        return pn.Row(
            kpi("Total Revenue", f"£{total_revenue:,.0f}", icon="payments"),
            kpi("Total Orders", f"{total_orders:,}", icon="shopping_cart"),
            kpi("Total Customers", f"{total_customers:,}", icon="groups"),
            kpi("Avg Order Value", f"£{avg_order_value:,.2f}", icon="trending_up"),
            sizing_mode="stretch_width",
        )

    @pn.depends(filtered_retail)
    def revenue_trend(d: pd.DataFrame):
        if d.empty:
            return pn.pane.Markdown("_No revenue data for current filters._")

        # recompute monthly revenue from filtered retail
        m = (
            d.groupby(d["InvoiceDate"].dt.to_period("M"))["TotalAmount"]
            .sum()
            .reset_index()
        )
        m["Month"] = m["InvoiceDate"].dt.to_timestamp()

        peak_row = m.loc[m["TotalAmount"].idxmax()]
        avg_rev = m["TotalAmount"].mean()

        line = m.hvplot.line(
            x="Month",
            y="TotalAmount",
            title="Monthly Revenue",
            line_width=3,
            color="#64B5F6",
            height=350,
        ).opts(transition=200)

        info = pn.pane.Markdown(
            f"**Peak month:** {peak_row['Month'].strftime('%Y-%m')}  \n"
            f"**Avg monthly revenue:** £{avg_rev:,.0f}"
        )

        return pn.Column(line, info)

    @pn.depends(filtered_retail)
    def top_products(d: pd.DataFrame):
        if d.empty:
            return pn.pane.Markdown("_No product data for current filters._")

        prod = (
            d.groupby("Description")["TotalAmount"]
            .sum()
            .reset_index()
            .rename(columns={"TotalAmount": "Revenue"})
        )
        top = prod.nlargest(10, "Revenue")

        return top.hvplot.bar(
            x="Description",
            y="Revenue",
            title="Top 10 Products by Revenue",
            color="#26A69A",
            height=350,
            rot=45,
        ).opts(transition=200)

    @pn.depends(filtered_retail)
    def top_countries(d: pd.DataFrame):
        if d.empty:
            return pn.pane.Markdown("_No country data for current filters._")

        c = (
            d.groupby("Country")["TotalAmount"]
            .sum()
            .reset_index()
            .rename(columns={"TotalAmount": "Revenue"})
        )
        top = c.nlargest(10, "Revenue")

        return top.hvplot.bar(
            x="Country",
            y="Revenue",
            title="Top 10 Countries by Revenue",
            color="#4DD0E1",
            height=350,
            rot=45,
        ).opts(transition=200)

    @pn.depends(filtered_retail)
    def temporal_patterns(d: pd.DataFrame):
        if d.empty:
            return pn.pane.Markdown("_No temporal data for current filters._")

        dow = (
            d.groupby("DayOfWeek")["TotalAmount"]
            .sum()
            .reset_index()
            .rename(columns={"TotalAmount": "Revenue"})
        )
        hour = (
            d.groupby("Hour")["TotalAmount"]
            .sum()
            .reset_index()
            .rename(columns={"TotalAmount": "Revenue"})
        )

        dow_plot = dow.hvplot.bar(
            x="DayOfWeek",
            y="Revenue",
            title="Revenue by Day of Week",
            color="#81C784",
            height=300,
        ).opts(transition=200)

        hour_plot = hour.hvplot.line(
            x="Hour",
            y="Revenue",
            title="Revenue by Hour of Day",
            color="#FFB74D",
            line_width=3,
            height=300,
        ).opts(transition=200)

        return pn.Row(dow_plot, hour_plot, sizing_mode="stretch_width")

    @pn.depends(filtered_retail)
    def country_table(d: pd.DataFrame):
        if d.empty:
            return pn.pane.Markdown("_No country metrics for current filters._")

        grp = d.groupby("Country").agg(
            Revenue=("TotalAmount", "sum"),
            NumOrders=("InvoiceNo", "nunique"),
            NumCustomers=("CustomerID", "nunique"),
            ItemsSold=("Quantity", "sum"),
        ).reset_index()

        grp["AvgOrderValue"] = grp["Revenue"] / grp["NumOrders"]
        total_rev = grp["Revenue"].sum()
        grp["RevenuePct"] = grp["Revenue"] / total_rev * 100

        grp_sorted = grp.sort_values("Revenue", ascending=False)

        table = pn.widgets.DataFrame(
            grp_sorted,
            autosize_mode="fit_viewport",
            height=350,
        )

        def _download_event(event):
            buf = io.StringIO()
            grp_sorted.to_csv(buf, index=False)
            buf.seek(0)
            download_button.file = ("country_metrics.csv", buf.read())

        download_button = pn.widgets.FileDownload(
            label="Download Country Metrics CSV",
            button_type="primary",
            filename="country_metrics.csv",
        )
        download_button.on_click(_download_event)

        return pn.Column(download_button, table)

    @pn.depends(filtered_retail)
    def strategic_recommendations(d: pd.DataFrame):
        if d.empty:
            return pn.pane.Markdown("_No data available for recommendations._")

        # Simple heuristic-based text; you can refine later
        total_rev = d["TotalAmount"].sum()
        dow = (
            d.groupby("DayOfWeek")["TotalAmount"]
            .sum()
            .sort_values(ascending=False)
        )
        hour = (
            d.groupby("Hour")["TotalAmount"]
            .sum()
            .sort_values(ascending=False)
        )
        top_day = dow.index[0]
        top_hour = hour.index[0]

        md = f"""
### 📌 Strategic Recommendations

**Revenue Growth**
- Focus campaigns around high-performing day: **{top_day}**
- Increase marketing and promos around **hour {top_hour}:00**

**Market Focus**
- Prioritize top-revenue countries and monitor emerging ones.
- Use filtered views to identify underperforming regions.

**Optimization**
- Refine product mix based on top products.
- Align staffing and logistics with peak hours and days.

_Total revenue in current view: **£{total_rev:,.0f}**_
"""
        return pn.pane.Markdown(md)

    return pn.Column(
        "## Business Overview",
        pn.panel(kpi_row, loading_indicator=True, placeholder=skeleton_card()),
        pn.Spacer(height=10),
        pn.panel(revenue_trend, loading_indicator=True, placeholder=skeleton_card(height="360px")),
        pn.Spacer(height=10),
        pn.Row(
            pn.panel(top_products, loading_indicator=True, placeholder=skeleton_card(height="360px")),
            pn.panel(top_countries, loading_indicator=True, placeholder=skeleton_card(height="360px")),
            sizing_mode="stretch_width",
        ),
        pn.Spacer(height=10),
        pn.panel(temporal_patterns, loading_indicator=True, placeholder=skeleton_card(height="320px")),
        pn.Spacer(height=10),
        pn.panel(country_table, loading_indicator=True, placeholder=skeleton_card(height="380px")),
        pn.Spacer(height=10),
        pn.panel(strategic_recommendations, loading_indicator=True, placeholder=skeleton_card(height="160px")),
        sizing_mode="stretch_width",
    )
