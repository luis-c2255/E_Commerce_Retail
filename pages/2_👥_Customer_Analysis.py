import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from utils.data_processor import load_and_prepare_data, create_rfm_features
from utils.theme import Components, Colors, apply_chart_theme, init_page

# ===========================================================
# PAGE INITIALIZATION
# ===========================================================
init_page("Customer Analysis", "👥")

# ===========================================================
# LOAD DATA
# ===========================================================
@st.cache_data
def load_all_data():
    try:
        df = load_and_prepare_data()
        rfm = create_rfm_features(df)
        return df, rfm
    except Exception as e:
        st.error(f"Error loading data: {e}")
        st.info("Please run prepare_data.py first.")
        st.stop()

df, rfm = load_all_data()

# ===========================================================
# PAGE HEADER
# ===========================================================
st.markdown(
    Components.page_header(
        "👥 Customer Intelligence & RFM Analysis",
        "Understand and segment your customers for targeted strategies"
    ),
    unsafe_allow_html=True
)

# ===========================================================
# RFM INTRODUCTION
# ===========================================================
st.markdown(
    Components.insight_box(
        "🎯 What is RFM Analysis?",
        """
        <p><strong>RFM</strong> stands for Recency, Frequency, and Monetary value:</p>
        <ul>
            <li><strong>Recency:</strong> How recently did the customer purchase?</li>
            <li><strong>Frequency:</strong> How often do they purchase?</li>
            <li><strong>Monetary:</strong> How much do they spend?</li>
        </ul>
        <p>We use these metrics to segment customers and tailor marketing strategies for maximum impact.</p>
        """,
        "info"
    ),
    unsafe_allow_html=True
)

# ===========================================================
# KEY METRICS
# ===========================================================
st.markdown(
    Components.section_header("Customer Overview Metrics", "📊"),
    unsafe_allow_html=True
)

col1, col2, col3, col4 = st.columns(4)

total_customers = len(rfm)
avg_recency = rfm['Recency'].mean()
avg_frequency = rfm['Frequency'].mean()
avg_monetary = rfm['Monetary'].mean()

with col1:
    st.markdown(
        Components.metric_card(
            title="Total Customers",
            value=f"{total_customers:,}",
            delta="📈 Active customer base",
            delta_positive=True,
            icon="👥",
            card_type="primary"
        ),
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        Components.metric_card(
            title="Avg Recency",
            value=f"{avg_recency:.0f} days",
            delta="📅 Since last purchase",
            delta_positive=True,
            icon="📅",
            card_type="info"
        ),
        unsafe_allow_html=True
    )

with col3:
    st.markdown(
        Components.metric_card(
            title="Avg Frequency",
            value=f"{avg_frequency:.1f}",
            delta="🛒 Orders per customer",
            delta_positive=True,
            icon="🛒",
            card_type="success"
        ),
        unsafe_allow_html=True
    )

with col4:
    st.markdown(
        Components.metric_card(
            title="Avg Monetary",
            value=f"£{avg_monetary:,.0f}",
            delta="💰 Customer lifetime value",
            delta_positive=True,
            icon="💰",
            card_type="warning"
        ),
        unsafe_allow_html=True
    )

st.markdown("---")

# ===========================================================
# CUSTOMER SEGMENTATION
# ===========================================================
st.markdown(
    Components.section_header("Customer Segmentation Distribution", "📊"),
    unsafe_allow_html=True
)

col1, col2 = st.columns([1, 1])

# Segment distribution pie chart
with col1:
    st.markdown("### 🥧 Distribution by Segment")
    segment_counts = rfm['Segment'].value_counts().reset_index()
    segment_counts.columns = ['Segment', 'Count']
    
    fig_segments = px.pie(
        segment_counts,
        values='Count',
        names='Segment',
        color_discrete_sequence=Colors.CHART_COLORS
    )
    
    fig_segments = apply_chart_theme(fig_segments)
    fig_segments.update_traces(
        textposition='inside',
        textinfo='percent',
        hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
    )
    fig_segments.update_layout(height=450, title="Distribution by Segment")
    
    st.plotly_chart(fig_segments, use_container_width=True)

# Segment breakdown
with col2:
    st.markdown("### 📋 Segment Breakdown")
    # Create a more compact display
    segment_display = segment_counts.copy()
    segment_display['Percentage'] = (segment_display['Count'] / segment_display['Count'].sum() * 100).round(1)
    
    # Add visual indicators
    def get_emoji(segment):
        if 'Champions' in segment or 'Loyal' in segment:
            return '🏆'
        elif 'Risk' in segment or 'Lost' in segment:
            return '⚠️'
        elif 'New' in segment:
            return '🆕'
        else:
            return '📊'
    
    segment_display['Icon'] = segment_display['Segment'].apply(get_emoji)
    
    # Display as styled dataframe
    st.dataframe(
        segment_display[['Icon', 'Segment', 'Count', 'Percentage']].style
        .format({'Count': '{:,}', 'Percentage': '{:.1f}%'})
        .background_gradient(subset=['Count'], cmap='Blues')
        .set_properties(**{
            'text-align': 'left',
            'font-size': '0.95rem',
            'padding': '8px'
        }),
        use_container_width=True,
        height=400,
        hide_index=True
    )
    
    # Add summary stats below
    st.markdown(f"""
    <div style='background-color: rgba(58, 141, 255, 0.1); padding: 1rem; 
                border-radius: 8px; margin-top: 1rem; border-left: 4px solid #3A8DFF;'>
        <p style='margin: 0; font-size: 0.9rem;'>
            <strong>Total Segments:</strong> {len(segment_counts)}<br>
            <strong>Largest:</strong> {segment_counts.iloc[0]['Segment']} ({segment_counts.iloc[0]['Count']:,})<br>
            <strong>Smallest:</strong> {segment_counts.iloc[-1]['Segment']} ({segment_counts.iloc[-1]['Count']:,})
        </p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ===========================================================
# RFM SEGMENTATION MAP
# ===========================================================
st.markdown(
    Components.section_header("RFM Segmentation Map", "🎯"),
    unsafe_allow_html=True
)

st.markdown(
    Components.insight_box(
        "💡 How to Read This Chart",
        """
        <p>This scatter plot shows the relationship between purchase frequency and total spending.</p>
        <ul>
            <li><strong>X-axis:</strong> How often customers purchase</li>
            <li><strong>Y-axis:</strong> How much customers spend in total</li>
            <li><strong>Bubble size:</strong> Recency (larger = purchased longer ago)</li>
            <li><strong>Color:</strong> Customer segment</li>
        </ul>
        <p><strong>Top-right quadrant</strong> = Your most valuable customers (high frequency + high spending)!</p>
        """,
        "info"
    ),
    unsafe_allow_html=True
)

fig_rfm = px.scatter(
    rfm,
    x='Frequency',
    y='Monetary',
    color='Segment',
    size='Recency',
    hover_data=['CustomerID', 'Recency', 'Frequency', 'Monetary'],
    labels={
        'Frequency': 'Purchase Frequency (# of Orders)',
        'Monetary': 'Total Spend (£)',
        'Recency': 'Days Since Last Purchase'
    },
    color_discrete_sequence=Colors.CHART_COLORS
)

fig_rfm = apply_chart_theme(fig_rfm)
fig_rfm.update_layout(height=600, title="RFM Segmentation Map")
fig_rfm.update_traces(marker=dict(line=dict(width=0.5, color='white')))

st.plotly_chart(fig_rfm, use_container_width=True)

st.markdown("---")

# ===========================================================
# RFM METRICS DISTRIBUTION
# ===========================================================
st.markdown(
    Components.section_header("RFM Metrics Distribution", "📊"),
    unsafe_allow_html=True
)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 📅 Recency Distribution")
    fig_r = px.histogram(
        rfm,
        x='Recency',
        nbins=30,
        labels={'Recency': 'Days Since Last Purchase'}
    )
    fig_r = apply_chart_theme(fig_r)
    fig_r.update_traces(marker_color=Colors.CHART_COLORS[0])
    fig_r.update_layout(height=350, showlegend=False, title="Recency Distribution")
    st.plotly_chart(fig_r, use_container_width=True)

with col2:
    st.markdown("### 🛒 Frequency Distribution")
    fig_f = px.histogram(
        rfm,
        x='Frequency',
        nbins=30,
        labels={'Frequency': 'Number of Orders'}
    )
    fig_f = apply_chart_theme(fig_f)
    fig_f.update_traces(marker_color=Colors.CHART_COLORS[1])
    fig_f.update_layout(height=350, showlegend=False, title="Frequency Distribution")
    st.plotly_chart(fig_f, use_container_width=True)

with col3:
    st.markdown("### 💰 Monetary Distribution")
    fig_m = px.histogram(
        rfm,
        x='Monetary',
        nbins=30,
        labels={'Monetary': 'Total Spend (£)'}
    )
    fig_m = apply_chart_theme(fig_m)
    fig_m.update_traces(marker_color=Colors.CHART_COLORS[2])
    fig_m.update_layout(height=350, showlegend=False, title="Monetary Distribution")
    st.plotly_chart(fig_m, use_container_width=True)

st.markdown("---")

# ===========================================================
# SEGMENT INSIGHTS & RECOMMENDATIONS
# ===========================================================
st.markdown(
    Components.section_header("Segment Insights & Action Plans", "💡"),
    unsafe_allow_html=True
)

# Calculate segment statistics
segment_stats = rfm.groupby('Segment').agg({
    'Recency': 'mean',
    'Frequency': 'mean',
    'Monetary': 'mean',
    'CustomerID': 'count'
}).reset_index()
segment_stats.columns = ['Segment', 'Avg Recency', 'Avg Frequency', 'Avg Monetary', 'Customer Count']

# Recommendations dictionary
recommendations = {
    'Champions': {
        'icon': '🏆',
        'description': 'Your best customers! High frequency, high spend, recent purchases.',
        'actions': [
            'Reward with exclusive VIP programs',
            'Early access to new products',
            'Request testimonials and referrals',
            'Personal account management'
        ],
        'priority': 'HIGHEST',
        'box_type': 'success'
    },
    'Loyal Customers': {
        'icon': '💎',
        'description': 'Highly engaged customers with consistent purchasing behavior.',
        'actions': [
            'Upsell premium products',
            'Cross-sell complementary items',
            'Loyalty point bonuses',
            'Birthday/anniversary rewards'
        ],
        'priority': 'HIGH',
        'box_type': 'success'
    },
    'Potential Loyalists': {
        'icon': '⭐',
        'description': 'Recent customers showing strong potential.',
        'actions': [
            'Nurture with personalized emails',
            'Product recommendations',
            'Welcome discount for 2nd purchase',
            'Educational content'
        ],
        'priority': 'MEDIUM',
        'box_type': 'info'
    },
    'Promising': {
        'icon': '🌱',
        'description': 'Good potential customers who need engagement.',
        'actions': [
            'Increase purchase frequency campaigns',
            'Limited-time offers',
            'Product bundles',
            'Social proof and reviews'
        ],
        'priority': 'MEDIUM',
        'box_type': 'info'
    },
    'At Risk': {
        'icon': '⚠️',
        'description': "Previously good customers who haven't purchased recently.",
        'actions': [
            'Win-back email campaigns',
            'Special reactivation discounts',
            'Survey to understand issues',
            'Personalized outreach'
        ],
        'priority': 'URGENT',
        'box_type': 'warning'
    },
    'Hibernating': {
        'icon': '😴',
        'description': 'Previously active customers now dormant.',
        'actions': [
            'Deep discount win-back offers',
            'Product updates and improvements',
            'Remind of past purchases',
            'Last chance campaigns'
        ],
        'priority': 'HIGH',
        'box_type': 'warning'
    },
    'Lost': {
        'icon': '❌',
        'description': 'Customers who have likely churned.',
        'actions': [
            'Final win-back attempt',
            'Aggressive discounts (50%+)',
            'Survey for feedback',
            'Consider cost-effectiveness'
        ],
        'priority': 'LOW',
        'box_type': 'error'
    },
    'New Customers': {
        'icon': '🆕',
        'description': 'Recent first-time buyers.',
        'actions': [
            'Welcome email series',
            'Onboarding programs',
            '2nd purchase incentive',
            'Product education'
        ],
        'priority': 'HIGH',
        'box_type': 'info'
    },
    'Others': {
        'icon': '📊',
        'description': 'Customers requiring further analysis.',
        'actions': [
            'Monitor behavior patterns',
            'General marketing campaigns',
            'Segment refinement',
            'Data quality check'
        ],
        'priority': 'LOW',
        'box_type': 'info'
    }
}

# Display segment insights
for segment in segment_stats['Segment']:
    stats = segment_stats[segment_stats['Segment'] == segment].iloc[0]
    rec = recommendations.get(segment, recommendations['Others'])
    
    with st.expander(f"{rec['icon']} {segment} - {int(stats['Customer Count']):,} customers ({rec['priority']} Priority)"):
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown(f"**{rec['description']}**")
            st.markdown("")
            st.markdown("**Segment Characteristics:**")
            st.markdown(f"""
            - 📅 Average Recency: **{stats['Avg Recency']:.0f} days**
            - 🛒 Average Frequency: **{stats['Avg Frequency']:.1f} orders**
            - 💰 Average Monetary: **£{stats['Avg Monetary']:,.2f}**
            """)
            st.markdown("")
            st.markdown("**Recommended Actions:**")
            for action in rec['actions']:
                st.markdown(f"- {action}")
        
        with col2:
            segment_customers = rfm[rfm['Segment'] == segment]
            st.markdown(
                Components.metric_card(
                    title="Customer Count",
                    value=f"{len(segment_customers):,}",
                    delta=f"{(len(segment_customers)/len(rfm)*100):.1f}% of total",
                    delta_positive=True,
                    icon="👥",
                    card_type=rec['box_type']
                ),
                unsafe_allow_html=True
            )
            st.markdown("")
            st.markdown(
                Components.metric_card(
                    title="Total Value",
                    value=f"£{segment_customers['Monetary'].sum():,.0f}",
                    delta="💰 Segment revenue",
                    delta_positive=True,
                    icon="💰",
                    card_type=rec['box_type']
                ),
                unsafe_allow_html=True
            )

st.markdown("---")

# ===========================================================
# TOP CUSTOMERS
# ===========================================================
st.markdown(
    Components.section_header("Top 20 Customers by Value", "🏆"),
    unsafe_allow_html=True
)

st.markdown(
    Components.insight_box(
        "💎 VIP Customers",
        "<p>These are your most valuable customers. Prioritize retention and satisfaction for maximum ROI.</p>",
        "success"
    ),
    unsafe_allow_html=True
)

top_customers = rfm.nlargest(20, 'Monetary')[
    ['CustomerID', 'Recency', 'Frequency', 'Monetary', 'Segment', 'Country']
]

st.dataframe(
    top_customers.style.format({
        'Recency': '{:.0f}',
        'Frequency': '{:.0f}',
        'Monetary': '£{:,.2f}'
    }).background_gradient(subset=['Monetary'], cmap='Greens'),
    use_container_width=True,
    height=500
)

st.markdown("---")

# ===========================================================
# STRATEGIC SUMMARY
# ===========================================================
st.markdown(
    Components.section_header("Strategic Summary", "🎯"),
    unsafe_allow_html=True
)

col1, col2, col3 = st.columns(3)

# Calculate key segments
champions_count = len(rfm[rfm['Segment'] == 'Champions'])
at_risk_count = len(rfm[rfm['Segment'] == 'At Risk'])

with col1:
    st.markdown(
        Components.insight_box(
            "🏆 Champions Focus",
            f"""
            <p><strong>{champions_count:,} Champions</strong> drive significant revenue.</p>
            <ul>
                <li>Maintain VIP treatment</li>
                <li>Build advocacy programs</li>
                <li>Leverage for referrals</li>
            </ul>
            """,
            "success"
        ),
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        Components.insight_box(
            "⚠️ Retention Alert",
            f"""
            <p><strong>{at_risk_count:,} At-Risk customers</strong> need attention.</p>
            <ul>
                <li>Launch win-back campaigns</li>
                <li>Personalized outreach</li>
                <li>Special reactivation offers</li>
            </ul>
            """,
            "warning"
        ),
        unsafe_allow_html=True
    )

with col3:
    st.markdown(
        Components.insight_box(
            "📊 Growth Opportunity",
            f"""
            <p>Convert <strong>Potential Loyalists</strong> into Champions.</p>
            <ul>
                <li>Increase engagement</li>
                <li>Upsell opportunities</li>
                <li>Loyalty programs</li>
            </ul>
            """,
            "info"
        ),
        unsafe_allow_html=True
    )

# ===========================================================
# FOOTER
# ===========================================================
st.markdown("---")
st.markdown(
    f"<p style='text-align: center; color: #5A6A7A;'>Customer analysis powered by RFM segmentation | " +
    f"Total customers analyzed: {len(rfm):,}</p>",
    unsafe_allow_html=True
)
