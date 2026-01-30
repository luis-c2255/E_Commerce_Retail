"""
Predictive Analytics - Sales Forecasting
Predict future sales and plan ahead with data-driven insights
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from utils.data_processor import load_and_prepare_data
from utils.ml_models import forecast_sales
from utils.theme import Components, Colors, apply_chart_theme, init_page

init_page("Predictive Analytics", "🔮")

@st.cache_data
def load_forecast_data():
    try:
        df = load_and_prepare_data()
        monthly_sales, forecast = forecast_sales(df, periods=12)
        return df, monthly_sales, forecast
    except Exception as e:
        st.error(f"Error: {e}")
        st.stop()

df, monthly_sales, forecast = load_forecast_data()

st.markdown(Components.page_header("🔮 Predictive Analytics - Sales Forecasting",
    "Predict future sales and plan ahead with data-driven insights"), unsafe_allow_html=True)

st.markdown(Components.insight_box("🎯 Why Sales Forecasting Matters",
    """<p>Accurate sales forecasts help you:</p>
    <ul><li>📦 Inventory Planning: Stock the right amount</li>
    <li>💰 Budget Allocation: Plan marketing budgets</li>
    <li>📈 Growth Strategy: Set realistic targets</li>
    <li>👥 Resource Planning: Prepare for demand</li></ul>""",
    "info"), unsafe_allow_html=True)

st.markdown(Components.section_header("Forecast Summary", "📊"), unsafe_allow_html=True)

hist_avg = monthly_sales.mean()
fore_avg = forecast['Forecast'].mean()
growth = ((fore_avg - hist_avg) / hist_avg) * 100
total_fore = forecast['Forecast'].sum()

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(Components.metric_card("Historical Avg/Month", f"£{hist_avg:,.0f}",
                "📊 Past baseline", True, "📊", "info"), unsafe_allow_html=True)
with col2:
    st.markdown(Components.metric_card("Forecast Avg/Month", f"£{fore_avg:,.0f}",
                "🔮 Predicted average", True, "🔮", "primary"), unsafe_allow_html=True)
with col3:
    st.markdown(Components.metric_card("Projected Growth", f"{growth:+.1f}%",
                "📈 vs historical", growth > 0, "📈" if growth > 0 else "📉",
                "success" if growth > 0 else "warning"), unsafe_allow_html=True)
with col4:
    st.markdown(Components.metric_card("12-Month Forecast", f"£{total_fore:,.0f}",
                "💰 Total projected", True, "💰", "success"), unsafe_allow_html=True)

st.markdown("---")
st.markdown(Components.section_header("12-Month Sales Forecast", "📈"), unsafe_allow_html=True)

st.markdown(Components.insight_box("📖 How to Read This Chart",
    """<ul><li><strong>Blue line:</strong> Historical actual sales</li>
    <li><strong>Orange line:</strong> Forecasted sales</li>
    <li><strong>Shaded area:</strong> Confidence interval (±15%)</li></ul>""",
    "info"), unsafe_allow_html=True)

fig_forecast = go.Figure()

fig_forecast.add_trace(go.Scatter(x=monthly_sales.index, y=monthly_sales.values,
    mode='lines+markers', name='Historical Sales',
    line=dict(color=Colors.BLUE_ENERGY, width=3), marker=dict(size=8)))

fig_forecast.add_trace(go.Scatter(x=forecast['Date'], y=forecast['Forecast'],
    mode='lines+markers', name='Forecasted Sales',
    line=dict(color='#FFB84D', width=3, dash='dash'), marker=dict(size=8)))

fig_forecast.add_trace(go.Scatter(
    x=forecast['Date'].tolist() + forecast['Date'].tolist()[::-1],
    y=forecast['Upper_Bound'].tolist() + forecast['Lower_Bound'].tolist()[::-1],
    fill='toself', fillcolor='rgba(255, 184, 77, 0.2)',
    line=dict(color='rgba(255,255,255,0)'), showlegend=True,
    name='Confidence Interval'))

fig_forecast = apply_chart_theme(fig_forecast)
fig_forecast.update_layout(title='Historical Sales and 12-Month Forecast',
    xaxis_title='Date', yaxis_title='Revenue (£)', height=550)
st.plotly_chart(fig_forecast, use_container_width=True)

st.markdown("---")
st.markdown(Components.section_header("Detailed Monthly Forecast", "📋"), unsafe_allow_html=True)

forecast_display = forecast.copy()
forecast_display['Date'] = forecast_display['Date'].dt.strftime('%B %Y')
forecast_display['MoM Growth'] = forecast_display['Forecast'].pct_change() * 100

st.dataframe(
    forecast_display[['Date', 'Forecast', 'Lower_Bound', 'Upper_Bound', 'MoM Growth']].style
    .format({'Forecast': '£{:,.2f}', 'Lower_Bound': '£{:,.2f}',
             'Upper_Bound': '£{:,.2f}', 'MoM Growth': '{:+.1f}%'})
    .background_gradient(subset=['Forecast'], cmap='Greens'),
    use_container_width=True, height=500
)

st.markdown("---")
st.markdown(Components.section_header("Seasonal Patterns Analysis", "🌡"), unsafe_allow_html=True)

monthly_df = pd.DataFrame({'Date': monthly_sales.index, 'Revenue': monthly_sales.values})
monthly_df['Month'] = monthly_df['Date'].dt.month_name()
month_order = ['January', 'February', 'March', 'April', 'May', 'June',
               'July', 'August', 'September', 'October', 'November', 'December']
seasonal = monthly_df.groupby('Month')['Revenue'].mean().reindex(month_order, fill_value=0)

fig_seasonal = px.bar(x=seasonal.index, y=seasonal.values,
    labels={'x': 'Month', 'y': 'Average Revenue (£)'})
fig_seasonal = apply_chart_theme(fig_seasonal)
fig_seasonal.update_traces(marker_color=Colors.CHART_COLORS)
fig_seasonal.update_layout(title='Average Revenue by Month', height=450, showlegend=False)
st.plotly_chart(fig_seasonal, use_container_width=True)

st.markdown("---")
st.markdown(Components.section_header("Strategic Recommendations", "🎯"), unsafe_allow_html=True)

peak_month = forecast.loc[forecast['Forecast'].idxmax()]
peak_name = peak_month['Date'].strftime('%B %Y')
peak_val = peak_month['Forecast']

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(Components.insight_box("📦 Inventory Management",
        f"<p><strong>Prepare for Peak:</strong> {peak_name}</p>"
        f"<p><strong>Expected:</strong> £{peak_val:,.0f}</p>"
        "<p><strong>Actions:</strong> Order 2-3 months ahead, stock 20-30% above forecast</p>",
        "success"), unsafe_allow_html=True)

with col2:
    st.markdown(Components.insight_box("💰 Budget Planning",
        f"<p><strong>12-Month Budget:</strong> £{total_fore:,.0f}</p>"
        f"<p><strong>Marketing:</strong> £{total_fore * 0.1:,.0f}</p>"
        "<p><strong>Allocate:</strong> 10% for marketing, 15% contingency, 5% for R&D</p>",
        "info"), unsafe_allow_html=True)

with col3:
    status = "success" if growth > 0 else "warning"
    st.markdown(Components.insight_box("📊 Performance Monitoring",
        f"<p><strong>Trend:</strong> {growth:+.1f}%</p>"
        "<br>"
        "<p><strong>Actions:</strong> Monthly reviews, adjust if >10% deviation, optimize development strategies.</p>",
        status), unsafe_allow_html=True)

# ===========================================================
# FOOTER
# ===========================================================
st.markdown("---")
st.markdown(f"<p style='text-align: center; color: #5A6A7A;'>Predictive Analytics | "
            f"12-month forecast | Growth: {growth:+.1f}% | Total: £{total_fore:,.0f}</p>",
            unsafe_allow_html=True)
