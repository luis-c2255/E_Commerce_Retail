import io
import itertools
import panel as pn
import hvplot.pandas  # noqa
import pandas as pd

from components.kpi_cards import kpi
from components.utils import load_clean_data
from components.skeleton import skeleton_card

pn.extension()

retail, month_metrics, product_metrics, country_metrics, rfm = load_clean_data()

def view(country_filter, date_range, customer_filter):

    # -----------------------------
    # 1. FILTERED RETAIL DATA
    # -----------------------------
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

    # -----------------------------
    # 2. BASKET KPIS
    # -----------------------------
    @pn.depends(filtered_retail)
    def basket_kpis(d: pd.DataFrame):
        if d.empty:
            return pn.Row("No basket data for current filters.")

        total_products = d["StockCode"].nunique()
        total_transactions = d["InvoiceNo"].nunique()

        basket_sizes = d.groupby("InvoiceNo")["Quantity"].sum()
        avg_basket_size = basket_sizes.mean()
        max_basket_size = basket_sizes.max()

        return pn.Row(
            kpi("Total Products", f"{total_products:,}", icon="inventory_2"),
            kpi("Total Transactions", f"{total_transactions:,}", icon="receipt_long"),
            kpi("Avg Basket Size", f"{avg_basket_size:.2f}", icon="shopping_bag"),
            kpi("Max Basket Size", f"{max_basket_size:.0f}", icon="shopping_cart_checkout"),
            sizing_mode="stretch_width",
        )

    # -----------------------------
    # 3. MOST POPULAR PRODUCTS
    # -----------------------------
    @pn.depends(filtered_retail)
    def popular_products(d: pd.DataFrame):
        if d.empty:
            return pn.pane.Markdown("_No product data for current filters._")

        prod = (
            d.groupby("Description")
            .agg(
                TotalQuantity=("Quantity", "sum"),
                Revenue=("TotalAmount", "sum"),
                NumOrders=("InvoiceNo", "nunique"),
            )
            .reset_index()
        )

        top_qty = prod.nlargest(20, "TotalQuantity")
        top_rev = prod.nlargest(10, "Revenue")

        qty_plot = top_qty.hvplot.bar(
            x="Description",
            y="TotalQuantity",
            title="Top 20 Products by Quantity",
            color="#26A69A",
            height=350,
            rot=60,
        ).opts(transition=200)

        rev_plot = top_rev.hvplot.bar(
            x="Description",
            y="Revenue",
            title="Top 10 Products by Revenue",
            color="#64B5F6",
            height=350,
            rot=60,
        ).opts(transition=200)

        return pn.Row(qty_plot, rev_plot, sizing_mode="stretch_width")

    # -----------------------------
    # 4. ASSOCIATION RULES WIDGETS
    # -----------------------------
    min_lift = pn.widgets.FloatSlider(
        name="Minimum Lift",
        start=1.0,
        end=5.0,
        step=0.1,
        value=1.5,
    )
    min_conf = pn.widgets.FloatSlider(
        name="Minimum Confidence (%)",
        start=10.0,
        end=100.0,
        step=5.0,
        value=40.0,
    )
    top_n_rules = pn.widgets.IntSlider(
        name="Number of Rules",
        start=5,
        end=50,
        step=5,
        value=10,
    )

    # -----------------------------
    # 5. ASSOCIATION RULES CALC
    # -----------------------------
    @pn.depends(filtered_retail, min_lift, min_conf, top_n_rules)
    def association_rules(d: pd.DataFrame, min_lift_val, min_conf_val, top_n_val):
        if d.empty:
            return pn.pane.Markdown("_No transactions for current filters._")

        # Use unique products per transaction
        baskets = (
            d.groupby("InvoiceNo")["Description"]
            .apply(lambda x: sorted(set(x.dropna())))
        )

        n_transactions = len(baskets)
        if n_transactions == 0:
            return pn.pane.Markdown("_No transactions for current filters._")

        # Count single items
        item_counts = {}
        for items in baskets:
            for item in items:
                item_counts[item] = item_counts.get(item, 0) + 1

        # Count pairs
        pair_counts = {}
        for items in baskets:
            for a, b in itertools.combinations(items, 2):
                pair = tuple(sorted((a, b)))
                pair_counts[pair] = pair_counts.get(pair, 0) + 1

        if not pair_counts:
            return pn.pane.Markdown("_Not enough product combinations to build associations._")

        rows = []
        for (a, b), count_ab in pair_counts.items():
            support = count_ab / n_transactions
            support_pct = support * 100

            count_a = item_counts.get(a, 1)
            count_b = item_counts.get(b, 1)

            conf_ab = count_ab / count_a
            conf_ba = count_ab / count_b

            lift_ab = conf_ab / (count_b / n_transactions)
            lift_ba = conf_ba / (count_a / n_transactions)

            rows.append(
                {
                    "A": a,
                    "B": b,
                    "Support": support,
                    "SupportPct": support_pct,
                    "Confidence_A_to_B": conf_ab * 100,
                    "Confidence_B_to_A": conf_ba * 100,
                    "Lift_A_to_B": lift_ab,
                    "Lift_B_to_A": lift_ba,
                }
            )

        rules = pd.DataFrame(rows)

        rules_filtered = rules[
            (rules["Lift_A_to_B"] >= min_lift_val) &
            (rules["Confidence_A_to_B"] >= min_conf_val)
        ].sort_values("Lift_A_to_B", ascending=False)

        if rules_filtered.empty:
            return pn.pane.Markdown("_No rules match the current thresholds._")

        rules_top = rules_filtered.head(top_n_val)

        bar = rules_top.hvplot.bar(
            x="A",
            y="Lift_A_to_B",
            by="B",
            stacked=False,
            title="Top Associations by Lift (A → B)",
            height=350,
            rot=60,
            cmap="Category20",
        ).opts(transition=200)

        scatter = rules_top.hvplot.scatter(
            x="SupportPct",
            y="Confidence_A_to_B",
            size="Lift_A_to_B",
            color="Lift_A_to_B",
            cmap="Viridis",
            title="Association Quality: Support vs Confidence",
            height=350,
        ).opts(transition=200)

        table = pn.widgets.DataFrame(
            rules_top[
                [
                    "A",
                    "B",
                    "SupportPct",
                    "Confidence_A_to_B",
                    "Lift_A_to_B",
                ]
            ],
            autosize_mode="fit_viewport",
            height=300,
        )

        def _download(event):
            buf = io.StringIO()
            rules_top.to_csv(buf, index=False)
            buf.seek(0)
            download.file = ("association_rules.csv", buf.read())

        download = pn.widgets.FileDownload(
            label="Download Rules CSV",
            button_type="primary",
            filename="association_rules.csv",
        )
        download.on_click(_download)

        return pn.Column(
            pn.Row(bar, scatter, sizing_mode="stretch_width"),
            pn.Spacer(height=10),
            download,
            table,
        )

    # -----------------------------
    # 6. RECOMMENDED BUNDLES
    # -----------------------------
    @pn.depends(filtered_retail)
    def recommended_bundles(d: pd.DataFrame):
        if d.empty:
            return pn.pane.Markdown("_No data for bundle recommendations._")

        baskets = (
            d.groupby("InvoiceNo")["Description"]
            .apply(lambda x: sorted(set(x.dropna())))
        )

        pair_counts = {}
        for items in baskets:
            for a, b in itertools.combinations(items, 2):
                pair = tuple(sorted((a, b)))
                pair_counts[pair] = pair_counts.get(pair, 0) + 1

        if not pair_counts:
            return pn.pane.Markdown("_Not enough product combinations for bundles._")

        top_pairs = sorted(pair_counts.items(), key=lambda x: x[1], reverse=True)[:5]

        md = "### 🎁 Recommended Product Bundles\n\n"
        for (a, b), count in top_pairs:
            md += f"- **{a}** + **{b}**  — frequently bought together ({count} baskets)\n"

        md += "\nConsider creating bundles with 15–20% discounts and featuring them in emails and on product pages."

        return pn.pane.Markdown(md)

    # -----------------------------
    # 7. ACTIONABLE INSIGHTS
    # -----------------------------
    @pn.depends(filtered_retail)
    def actionable_insights(d: pd.DataFrame):
        if d.empty:
            return pn.pane.Markdown("_No data available for insights._")

        n_tx = d["InvoiceNo"].nunique()
        n_prod = d["StockCode"].nunique()

        md = f"""
### 📌 Actionable Insights

- You currently have **{n_tx:,}** transactions and **{n_prod:,}** unique products in view.
- Use association rules to:
  - Design **product bundles** for cross‑sell and upsell.
  - Optimize **store layout** or **recommendation carousels**.
  - Enhance **email campaigns** with "Frequently bought together" suggestions.

Use the sliders above to explore stronger or weaker associations by adjusting **lift**, **confidence**, and **number of rules**.
"""
        return pn.pane.Markdown(md)

    # -----------------------------
    # PAGE LAYOUT
    # -----------------------------
    controls = pn.Card(
        "### Association Rule Filters",
        min_lift,
        min_conf,
        top_n_rules,
        collapsed=False,
        sizing_mode="stretch_width",
    )

    return pn.Column(
        "## Basket Analysis",
        pn.panel(basket_kpis, loading_indicator=True, placeholder=skeleton_card()),
        pn.Spacer(height=10),
        pn.panel(popular_products, loading_indicator=True, placeholder=skeleton_card(height="380px")),
        pn.Spacer(height=10),
        controls,
        pn.Spacer(height=5),
        pn.panel(association_rules, loading_indicator=True, placeholder=skeleton_card(height="420px")),
        pn.Spacer(height=10),
        pn.panel(recommended_bundles, loading_indicator=True, placeholder=skeleton_card(height="200px")),
        pn.Spacer(height=10),
        pn.panel(actionable_insights, loading_indicator=True, placeholder=skeleton_card(height="200px")),
        sizing_mode="stretch_width",
    )
