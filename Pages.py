"""
Retail Analytics Dashboard - Main Entry Point
A comprehensive analytics platform for e-commerce insights
"""

import streamlit as st
import pandas as pd
import sys
import os

# Configure page
st.set_page_config(
    page_title="Retail Analytics Dashboard",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)
 # Add sidebar toggle button fix
st.markdown("""
        <style>
        /* Ensure sidebar is always accessible */
        [data-testid="stSidebar"] {
            display: block !important;
            visibility: visible !important;
        }
        
        /* Sidebar toggle arrow */
        [data-testid="collapsedControl"] {
            display: block !important;
            visibility: visible !important;
            background-color: #3A8DFF !important;
            color: white !important;
            border: 2px solid white !important;
            border-radius: 5px !important;
            padding: 10px !important;
            font-size: 20px !important;
            cursor: pointer !important;
            z-index: 999999 !important;
        }
        /* Sidebar navigation */
        [data-testid="stSidebarNav"] {
            display: block !important;
            background-color: rgba(138, 176, 171, 0.15) !important;
        }
        /* Sidebar expand/collapse button */
        button[kind="header"] {
            background-color: #3A8DFF !important;
            color: white !important;
            border: 2px solid white !important;
        }
        </style>
        
    """, unsafe_allow_html=True)
# Main page content

# Load custom CSS
try:
    with open('style.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
except FileNotFoundError:
    st.warning("Custom CSS file not found. Using default styling.")

# Main page content
st.markdown("""
<div style='text-align: center; padding: 2rem 0;'>
    <h1 style='color: #3A8DFF; font-size: 3rem; margin-bottom: 0.5rem;'>
        🛒 Retail Analytics Dashboard
    </h1>
    <p style='font-size: 1.2rem; color: #5A6A7A; margin-bottom: 2rem;'>
        Comprehensive insights to drive your e-commerce success
    </p>
</div>
""", unsafe_allow_html=True)

# Welcome section
col1, col2, col3 = st.columns(3, vertical_alignment="center", gap="small")

with col1:
    st.markdown("""
    <div style='background-color: #1E1E1E; padding: 1rem; border-radius: 10px; border-top: 4px solid #3A8DFF; min-height: 180px;
    display: flex; flex-direction: column;'>
        <h3 style='color: #3A8DFF; margin-top: 0;'>📊 Overview</h3
        <p style='flex-grow: 1;'>Get a comprehensive view of your business performance with key metrics, trends, and insights.</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style='background-color: #1E1E1E; padding: 1rem; border-radius: 10px; border-top: 4px solid #4CC9A6; min-height: 180px; 
    display: flex; flex-direction: column;'>
        <h3 style='color: #4CC9A6; margin-top: 0;'>👥 Customer Intelligence</h3>
        <p style='flex-grow: 1;'>Understand your customers with RFM analysis, segmentation, and behavioral insights.</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div style='background-color: #1E1E1E; padding: 1rem; border-radius: 10px; border-top: 4px solid #FFB84D; min-height: 180px;
    display: flex; flex-direction: column;'>
        <h3 style='color: #FFB84D; margin-top: 0;'>🔮 Predictive Analytics</h3>
        <p style='flex-grow: 1;'>Forecast future sales, predict churn, and calculate customer lifetime value.</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Feature highlights
st.markdown("### 🚀 Available Analytics Modules")

features = {
    "📊 Business Overview": "Revenue trends, top products, geographic analysis, and temporal patterns",
    "👥 Customer Analysis": "RFM segmentation, customer insights, and actionable recommendations",
    "🛒 Basket Analysis": "Product associations, cross-selling opportunities, and bundle recommendations",
    "📈 Cohort Analysis": "Customer retention tracking, cohort performance, and lifecycle insights",
    "🔮 Predictive Analytics": "Sales forecasting, seasonal patterns, and growth projections",
    "💰 CLV & Churn": "Customer lifetime value prediction, churn risk analysis, and retention strategies"
}

col1, col2 = st.columns(2)
items = list(features.items())

for i, (title, description) in enumerate(items):
    col = col1 if i % 2 == 0 else col2
    with col:
        st.markdown(f"""
        <div style='background-color: rgba(58, 141, 255, 0.1); padding: 1rem; 
                    border-radius: 8px; margin-bottom: 1rem; border-left: 4px solid #3A8DFF;'>
            <p style='margin: 0;'><strong>{title}</strong></p>
            <p style='margin: 0.5rem 0 0 0; color: #FAFAFF; font-size: 0.9rem;'>{description}</p>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# Getting started
st.markdown("### 🎯 Getting Started")
st.markdown("""
<div style='background-color: rgba(76, 201, 166, 0.15); padding: 1.5rem; 
            border-radius: 8px; border-left: 6px solid #4CC9A6;'>
    <p style='margin: 0;'><strong>👈 Use the sidebar navigation</strong> to explore different analysis modules.</p>
    <p style='margin: 0.5rem 0 0 0;'>Each module provides interactive visualizations, detailed insights, 
    and actionable recommendations to help you make data-driven decisions.</p>
</div>
""", unsafe_allow_html=True)

# Data info
st.markdown("---")
st.markdown("### 📊 Data Overview")

try:
    # Try to load data to show stats
    from utils.data_processor import load_and_prepare_data
    
    if 'df' not in st.session_state:
        with st.spinner("Loading data..."):
            st.session_state.df = load_and_prepare_data()
    
    df = st.session_state.df
    
    col1, col2, col3 = st.columns(3, border=True, vertical_alignment="center") 
        
    with col1:
        st.metric("Total Transactions", f"{len(df):,}", height="stretch", width="stretch")
        
    with col2:
        st.metric("Unique Customers", f"{df['CustomerID'].nunique():,}", height="stretch", width="stretch")
        
    with col3:
        st.metric("Products", f"{df['Description'].nunique():,}", height="stretch", width="stretch")

    #with col4:
        #date_range = f"{df['InvoiceDate'].min().strftime('%Y-%m-%d')} to {df['InvoiceDate'].max().strftime('%Y-%m-%d')}"
        #st.metric("Date Range", date_range, height="stretch", width="stretch")
        
except Exception as e:
    st.info("💡 Data will be loaded when you navigate to analysis pages.")

# Footer
st.markdown("---")
st.markdown("""
<p style='text-align: center; color: #5A6A7A; font-size: 0.9rem;'>
    Built with ❤️ using Streamlit | Powered by Advanced Analytics & Machine Learning
</p>
""", unsafe_allow_html=True)
