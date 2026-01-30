"""
Basket Analysis - Market Basket Analysis & Product Associations
Discover cross-selling opportunities and product bundling strategies
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from utils.data_processor import load_and_prepare_data, prepare_basket_analysis
from utils.ml_models import market_basket_analysis
from utils.theme import Components, Colors, apply_chart_theme, init_page

init_page("Basket Analysis", "🛒")

@st.cache_data
def load_basket_data():
    try:
        df = load_and_prepare_data()
        basket_binary = prepare_basket_analysis(df)
        frequent_items, pairs = market_basket_analysis(basket_binary, min_support=0.01)
        return df, basket_binary, frequent_items, pairs
    except Exception as e:
        st.error(f"Error: {e}")
        st.stop()

df, basket_binary, frequent_items, pairs = load_basket_data()

st.markdown(
    Components.page_header(
        "🛒 Market Basket Analysis",
        "Discover product associations and unlock cross-selling opportunities"
    ),
    unsafe_allow_html=True
)

st.markdown(
    Components.insight_box(
        "🎯 What is Market Basket Analysis?",
        """
        <p>Market Basket Analysis reveals which products are frequently purchased together, enabling you to:</p>
        <ul>
            <li><strong>📦 Product Placement:</strong> Place related items near each other</li>
            <li><strong>🎁 Cross-selling:</strong> Recommend complementary products</li>
            <li><strong>💰 Promotions:</strong> Create bundles of frequently co-purchased items</li>
        </ul>
        """,
        "info"
    ),
    unsafe_allow_html=True
)

st.markdown(Components.section_header("Basket Overview Metrics", "📊"), unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(Components.metric_card("Total Products", f"{basket_binary.shape[1]:,}", 
                "📦 Unique items", True, "📦", "primary"), unsafe_allow_html=True)
with col2:
    st.markdown(Components.metric_card("Total Transactions", f"{basket_binary.shape[0]:,}", 
                "🛒 Completed orders", True, "🛒", "info"), unsafe_allow_html=True)
with col3:
    st.markdown(Components.metric_card("Avg Basket Size", f"{basket_binary.sum(axis=1).mean():.1f}", 
                "📊 Items per order", True, "📊", "success"), unsafe_allow_html=True)
with col4:
    st.markdown(Components.metric_card("Max Basket Size", f"{int(basket_binary.sum(axis=1).max())}", 
                "🎯 Largest order", True, "🎯", "warning"), unsafe_allow_html=True)

st.markdown("---")
st.markdown(Components.section_header("Most Frequently Purchased Products", "📊"), unsafe_allow_html=True)


with st.container():
    st.markdown("### 📊 Top 20 Most Popular Products")
    top_items = frequent_items.head(20)
    top_items_df = pd.DataFrame({'Product': top_items.index, 'Frequency': top_items.values * 100})
    
    fig_items = px.bar(top_items_df, x='Frequency', y='Product', orientation='h',
                       labels={'Frequency': 'Purchase Frequency (%)', 'Product': 'Product'})
    fig_items = apply_chart_theme(fig_items)
    fig_items.update_traces(marker_color=Colors.MINT_LEAF)
    fig_items.update_layout(height=600, showlegend=False, title="Top 20 Most Popular Products")
    st.plotly_chart(fig_items, use_container_width=True)

with st.container():
    st.markdown("### 🏆 Top 10 Products")
    st.markdown("*Most frequently purchased items*")
    
    # Create compact table
    top_10_items = frequent_items.head(10).reset_index()
    top_10_items.columns = ['Product', 'Frequency']
    top_10_items['Frequency %'] = (top_10_items['Frequency'] * 100).round(1)
    top_10_items['Orders'] = (top_10_items['Frequency'] * basket_binary.shape[0]).astype(int)
    top_10_items['Rank'] = range(1, 11)
    
    # Add medal emojis
    def get_medal(rank):
        if rank == 1: return '🥇'
        elif rank == 2: return '🥈'
        elif rank == 3: return '🥉'
        else: return f'{rank}.'
    
    top_10_items[''] = top_10_items['Rank'].apply(get_medal)
    
    # Truncate product names
    top_10_items['Product'] = top_10_items['Product'].str[:35] + '...'
    
    st.dataframe(
        top_10_items[['', 'Product', 'Frequency %', 'Orders']].style
        .format({'Frequency %': '{:.1f}%', 'Orders': '{:,}'})
        .background_gradient(subset=['Frequency %'], cmap='Greens')
        .set_properties(**{
            'text-align': 'left',
            'font-size': '0.9rem',
            'padding': '6px'
        }),
        use_container_width=True,
        height=400,
        hide_index=True
    )
    
    # Add insights
    top_item = top_10_items.iloc[0]
    st.markdown(f"""
    <div style='background-color: rgba(76, 201, 166, 0.1); padding: 0.8rem; 
                border-radius: 8px; margin-top: 1rem; border-left: 4px solid #4CC9A6;'>
        <p style='margin: 0; font-size: 0.85rem;'>
            <strong>💡 Top Item:</strong> {top_item['Product'][:30]}<br>
            <strong>Appears in:</strong> {top_item['Frequency %']:.1f}% of transactions<br>
            <strong>Total orders:</strong> {top_item['Orders']:,}
        </p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")
st.markdown(Components.section_header("Product Association Rules", "🔗"), unsafe_allow_html=True)

st.markdown(
    Components.insight_box(
        "📚 Understanding the Metrics",
        """
        <ul>
            <li><strong>Support:</strong> How often items appear together (%)</li>
            <li><strong>Confidence:</strong> When A is purchased, likelihood of buying B (%)</li>
            <li><strong>Lift:</strong> How much more likely items are bought together (>1 = strong association)</li>
        </ul>
        """,
        "info"
    ),
    unsafe_allow_html=True
)

col1, col2, col3 = st.columns(3)
with col1:
    min_lift = st.slider("Minimum Lift", 1.0, 5.0, 1.5, 0.1)
with col2:
    min_confidence = st.slider("Minimum Confidence (%)", 0, 100, 20, 5)
with col3:
    max_rules = st.number_input("Rules to Display", 5, 50, 20, 5)

filtered_pairs = pairs[(pairs['Lift'] >= min_lift) & (pairs['Confidence_A_to_B'] >= min_confidence / 100)]

st.markdown(f"### 📋 Top {max_rules} Association Rules")
st.markdown(f"*Found {len(filtered_pairs):,} rules matching your criteria*")

if len(filtered_pairs) > 0:
    display_pairs = filtered_pairs.head(max_rules).copy()
    display_pairs['Rule'] = display_pairs.apply(lambda r: f"{r['Item_A'][:30]} → {r['Item_B'][:30]}", axis=1)
    display_pairs['Support (%)'] = (display_pairs['Support'] * 100).round(2)
    display_pairs['Confidence (%)'] = (display_pairs['Confidence_A_to_B'] * 100).round(2)
    display_pairs['Lift Score'] = display_pairs['Lift'].round(2)
    
    st.dataframe(
        display_pairs[['Rule', 'Support (%)', 'Confidence (%)', 'Lift Score']].style
        .background_gradient(subset=['Lift Score'], cmap='Greens')
        .format({'Support (%)': '{:.2f}%', 'Confidence (%)': '{:.2f}%', 'Lift Score': '{:.2f}'}),
        use_container_width=True, height=450
    )
    
    st.markdown("### 📊 Top 10 Associations by Lift Score")
    top_assoc = filtered_pairs.head(10).copy()
    top_assoc['Rule_Short'] = top_assoc.apply(lambda r: f"{r['Item_A'][:20]}... → {r['Item_B'][:20]}...", axis=1)
    
    fig_lift = px.bar(top_assoc, x='Lift', y='Rule_Short', orientation='h')
    fig_lift = apply_chart_theme(fig_lift)
    fig_lift.update_traces(marker_color=Colors.BLUE_ENERGY)
    fig_lift.update_layout(height=500, showlegend=False, title="Top 10 Associations by Lift Score")
    st.plotly_chart(fig_lift, use_container_width=True)
else:
    st.markdown(Components.insight_box("⚠️ No Rules Found",
        f"<p>No rules found with Lift ≥ {min_lift} and Confidence ≥ {min_confidence}%</p>", "warning"),
        unsafe_allow_html=True)

st.markdown("---")
st.markdown(Components.section_header("Business Recommendations", "💡"), unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(Components.insight_box("🎁 Product Bundling",
        "<ul><li>Create bundles from top associated products</li><li>Offer 15-20% bundle discounts</li></ul>",
        "success"), unsafe_allow_html=True)
with col2:
    st.markdown(Components.insight_box("🏪 Store Layout",
        "<ul><li>Place associated products near each other</li><li>Create themed zones</li></ul>",
        "info"), unsafe_allow_html=True)
with col3:
    st.markdown(Components.insight_box("📱 Recommendations",
        "<ul><li>'Customers also bought' suggestions</li><li>Personalized emails</li></ul>",
        "warning"), unsafe_allow_html=True)
        
# ===========================================================
# FOOTER
# ===========================================================
st.markdown("---")
st.markdown(f"<p style='text-align: center; color: #5A6A7A;'>Market Basket Analysis | "
            f"{len(filtered_pairs):,} association rules</p>", unsafe_allow_html=True)
