import io
import panel as pn
import hvplot.pandas  # noqa
import pandas as pd

from components.kpi_cards import kpi
from components.utils import load_clean_data
from components.skeleton import skeleton_card

pn.extension()

# Load all datasets
retail, month_metrics, product_metrics, country_metrics, rfm = load_clean_data()

def view(country_filter, date_range, customer_filter):

    # -----------------------------
    # 1. FILTERED RFM DATA
    # -----------------------------
    @pn.depends(country_filter, date_range, customer_filter)
    def filtered_rfm():
        d = rfm.copy()

        if country_filter.value:
            d = d[d["Country"].isin(country_filter.value)]

        if customer_filter.value:
            d = d[d["CustomerID"].isin(customer_filter.value)]

        # Date range filtering based on LastPurchase
        start, end = date_range.value
        d = d[(pd.to_datetime(d["LastPurchase"]) >= start) &
              (pd.to_datetime(d["LastPurchase"]) <= end)]

        return d

    # -----------------------------
    # 2. KPI ROW
    # -----------------------------
    @pn.depends(filtered_rfm)
    def kpi_row(d: pd.DataFrame):
        if d.empty:
            return pn.Row("No customer data for current filters.")

        total_customers = d["CustomerID"].nunique()
        avg_recency = d["Recency"].mean()
        avg_frequency = d["Frequency"].mean()
        avg_monetary = d["Monetary"].mean()

        return pn.Row(
            kpi("Total Customers", f"{total_customers:,}", icon="groups"),
            kpi("Avg Recency", f"{avg_recency:.1f} days", icon="schedule"),
            kpi("Avg Frequency", f"{avg_frequency:.2f}", icon="repeat"),
            kpi("Avg Monetary", f"£{avg_monetary:,.2f}", icon="payments"),
            sizing_mode="stretch_width",
        )

    # -----------------------------
    # 3. SEGMENT DISTRIBUTION
    # -----------------------------
    @pn.depends(filtered_rfm)
    def segment_distribution(d: pd.DataFrame):
        if d.empty:
            return pn.pane.Markdown("_No segment data for current filters._")

        seg = d["Segment"].value_counts().reset_index()
        seg.columns = ["Segment", "Count"]

        return seg.hvplot.bar(
            x="Segment",
            y="Count",
            title="Customer Segment Distribution",
            color="#64B5F6",
            height=350,
            rot=45,
        ).opts(transition=200)

    # -----------------------------
    # 4. RFM SEGMENTATION MAP
    # -----------------------------
    @pn.depends(filtered_rfm)
    def rfm_map(d: pd.DataFrame):
        if d.empty:
            return pn.pane.Markdown("_No RFM data for current filters._")

        return d.hvplot.scatter(
            x="Frequency",
            y="Monetary",
            c="Segment",
            size="Recency",
            title="RFM Segmentation Map",
            height=400,
            cmap="Category20",
            alpha=0.8,
        ).opts(transition=200)

    # -----------------------------
    # 5. RFM DISTRIBUTIONS
    # -----------------------------
    @pn.depends(filtered_rfm)
    def rfm_distributions(d: pd.DataFrame):
        if d.empty:
            return pn.pane.Markdown("_No distribution data for current filters._")

        rec = d.hvplot.hist("Recency", bins=20, color="#26A69A", title="Recency Distribution", height=300)
        freq = d.hvplot.hist("Frequency", bins=20, color="#4DD0E1", title="Frequency Distribution", height=300)
        mon = d.hvplot.hist("Monetary", bins=20, color="#81C784", title="Monetary Distribution", height=300)

        return pn.Row(rec, freq, mon, sizing_mode="stretch_width")

    # -----------------------------
    # 6. SEGMENT INSIGHTS
    # -----------------------------
    @pn.depends(filtered_rfm)
    def segment_insights(d: pd.DataFrame):
        if d.empty:
            return pn.pane.Markdown("_No segment insights available._")

        seg_counts = d["Segment"].value_counts()

        md = "### 🧠 Segment Insights\n\n"

        for seg, count in seg_counts.items():
            md += f"**{seg}** — {count} customers\n\n"

        return pn.pane.Markdown(md)

    # -----------------------------
    # 7. TOP CUSTOMERS
    # -----------------------------
    @pn.depends(filtered_rfm)
    def top_customers(d: pd.DataFrame):
        if d.empty:
            return pn.pane.Markdown("_No customer data for current filters._")

        top = d.nlargest(20, "Monetary")[["CustomerID", "Monetary", "Frequency", "Recency"]]

        table = pn.widgets.DataFrame(top, autosize_mode="fit_viewport", height=350)

        def _download(event):
            buf = io.StringIO()
            top.to_csv(buf, index=False)
            buf.seek(0)
            download.file = ("top_customers.csv", buf.read())

        download = pn.widgets.FileDownload(
            label="Download Top Customers CSV",
            button_type="primary",
            filename="top_customers.csv",
        )
        download.on_click(_download)

        return pn.Column(download, table)

    # -----------------------------
    # 8. STRATEGIC SUMMARY
    # -----------------------------
    @pn.depends(filtered_rfm)
    def strategic_summary(d: pd.DataFrame):
        if d.empty:
            return pn.pane.Markdown("_No strategic insights available._")

        champions = (d["Segment"] == "Champions").sum()
        at_risk = (d["Segment"] == "At Risk").sum()
        lost = (d["Segment"] == "Lost").sum()

        md = f"""
### 📌 Strategic Summary

**Champions:** {champions}  
These are your most valuable customers. Maintain VIP treatment and leverage them for referrals.

**At Risk:** {at_risk}  
Launch win‑back campaigns, personalized outreach, and reactivation offers.

**Lost:** {lost}  
Consider cost‑effective reactivation or focus resources elsewhere.

Use the filters to explore how customer behavior changes across countries, time periods, and customer segments.
"""

        return pn.pane.Markdown(md)

    # -----------------------------
    # PAGE LAYOUT
    # -----------------------------
    return pn.Column(
        "## Customer Analysis (RFM)",
        pn.panel(kpi_row, loading_indicator=True, placeholder=skeleton_card()),
        pn.Spacer(height=10),
        pn.panel(segment_distribution, loading_indicator=True, placeholder=skeleton_card(height="360px")),
        pn.Spacer(height=10),
        pn.panel(rfm_map, loading_indicator=True, placeholder=skeleton_card(height="420px")),
        pn.Spacer(height=10),
        pn.panel(rfm_distributions, loading_indicator=True, placeholder=skeleton_card(height="320px")),
        pn.Spacer(height=10),
        pn.panel(segment_insights, loading_indicator=True, placeholder=skeleton_card(height="200px")),
        pn.Spacer(height=10),
        pn.panel(top_customers, loading_indicator=True, placeholder=skeleton_card(height="380px")),
        pn.Spacer(height=10),
        pn.panel(strategic_summary, loading_indicator=True, placeholder=skeleton_card(height="200px")),
        sizing_mode="stretch_width",
    )
