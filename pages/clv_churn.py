import io
import panel as pn
import hvplot.pandas  # noqa
import pandas as pd
import shap

from components.kpi_cards import kpi
from components.utils import load_clean_data, compute_shap_values
from components.skeleton import skeleton_card
from sklearn.preprocessing import StandardScaler 

pn.extension("plotly")

retail, month_metrics, product_metrics, country_metrics, rfm = load_clean_data()

# Load model artifacts
rfm, clv_model, churn_model, clv_importance, churn_importance, clv_mae, churn_acc = load_clean_data()[4]

def view(country_filter, date_range, customer_filter):

    # -----------------------------
    # FILTERED DATA
    # -----------------------------
    @pn.depends(country_filter, date_range, customer_filter)
    def filtered_data():
        d = rfm.copy()

        if country_filter.value:
            d = d[d["Country"].isin(country_filter.value)]

        if customer_filter.value:
            d = d[d["CustomerID"].isin(customer_filter.value)]

        if "LastPurchase" in d.columns:
            start, end = date_range.value
            d = d[
                (pd.to_datetime(d["LastPurchase"]) >= start)
                & (pd.to_datetime(d["LastPurchase"]) <= end)
            ]

        return d

    # -----------------------------
    # MODEL PERFORMANCE CARDS
    # -----------------------------
    def model_performance_cards():
        return pn.Row(
            kpi("CLV MAE", f"£{clv_mae:,.0f}", icon="rule"),
            kpi("Churn Accuracy", f"{churn_acc*100:.1f}%", icon="verified"),
            sizing_mode="stretch_width",
        )

    # -----------------------------
    # FEATURE IMPORTANCE CHARTS
    # -----------------------------
    def feature_importance_charts():
        clv_plot = clv_importance.hvplot.bar(
            x="Feature", y="Importance",
            title="CLV Feature Importance",
            color="#64B5F6", height=350
        )

        churn_plot = churn_importance.hvplot.bar(
            x="Feature", y="Importance",
            title="Churn Feature Importance",
            color="#FFB74D", height=350
        )

        return pn.Row(clv_plot, churn_plot, sizing_mode="stretch_width")

    # -----------------------------
    # SHAP GLOBAL SUMMARY
    # -----------------------------
    def shap_global_summary():
        X = rfm[["Frequency", "AvgOrderValue", "Lifespan"]]
        shap_values = compute_shap_values(clv_model, StandardScaler().fit(X), X)

        fig = shap.summary_plot(shap_values, X, show=False)
        return pn.pane.Matplotlib(fig, tight=True, height=400)

    # -----------------------------
    # STRATEGIC 2×2 MATRIX
    # -----------------------------
    @pn.depends(filtered_data)
    def strategic_matrix(d):
        if d.empty:
            return pn.pane.Markdown("_No data available._")

        clv_q = d["Predicted_CLV"].quantile([0.33, 0.66])
        def clv_tier(v):
            if v <= clv_q.iloc[0]: return "Low CLV"
            if v <= clv_q.iloc[1]: return "Medium CLV"
            return "High CLV"

        d = d.copy()
        d["CLV_Tier"] = d["Predicted_CLV"].apply(clv_tier)

        risk_map = {"Low": 0, "Medium": 1, "High": 2}
        d["RiskNum"] = d["ChurnRisk"].map(risk_map)

        return d.hvplot.scatter(
            x="Predicted_CLV",
            y="RiskNum",
            c="CLV_Tier",
            cmap="Category10",
            alpha=0.7,
            height=380,
            title="Strategic Matrix: CLV × Churn Risk"
        )

    # -----------------------------
    # EXPORTABLE CUSTOMER LISTS
    # -----------------------------
    @pn.depends(filtered_data)
    def export_lists(d):
        if d.empty:
            return pn.pane.Markdown("_No customers available._")

        high_clv = d.nlargest(50, "Predicted_CLV")
        high_risk = d[d["ChurnRisk"] == "High"].nlargest(50, "Predicted_CLV")

        def make_download(df, label, filename):
            btn = pn.widgets.FileDownload(label=label, filename=filename, button_type="primary")
            def _dl(event):
                buf = io.StringIO()
                df.to_csv(buf, index=False)
                buf.seek(0)
                btn.file = (filename, buf.read())
            btn.on_click(_dl)
            return btn

        return pn.Column(
            "### Export Customer Lists",
            make_download(high_clv, "Download Top CLV Customers", "top_clv.csv"),
            make_download(high_risk, "Download High‑Risk Customers", "high_risk.csv"),
        )

    # -----------------------------
    # PAGE LAYOUT
    # -----------------------------
    return pn.Column(
        "## CLV & Churn Analysis (ML‑Powered)",
        model_performance_cards(),
        pn.Spacer(height=10),
        feature_importance_charts(),
        pn.Spacer(height=10),
        pn.panel(strategic_matrix, loading_indicator=True, placeholder=skeleton_card(height="380px")),
        pn.Spacer(height=10),
        export_lists(),
        sizing_mode="stretch_width",
    )
