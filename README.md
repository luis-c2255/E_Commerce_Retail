# 🛒 Retail Analytics Dashboard

![Static Badge](https://img.shields.io/badge/streamlit-app-red?logo=streamlit)
![Static Badge](https://img.shields.io/badge/python-3.10-blue?logo=python)
![Static Badge](https://img.shields.io/badge/License-MIT-orange)
![Static Badge](https://img.shields.io/badge/Plotly-charts-purple?logo=plotly)
![Static Badge](https://img.shields.io/badge/github-repo-green?logo=github)

![Cover](/utils/istockphoto-2061836383-612x612.svg)

A comprehensive, production-ready analytics dashboard for e-commerce businesses built with Streamlit, featuring advanced analytics, machine learning predictions, and interactive visualizations.

## ✨ Features

### 📊 **Business Overview**
- Key performance indicators (Revenue, Orders, Customers, AOV)
- Revenue trend analysis with interactive charts
- Top products and geographic performance
- Temporal patterns (hourly/daily sales patterns)
- Detailed performance metrics by country

### 👥 **Customer Analysis**
- RFM (Recency, Frequency, Monetary) segmentation
- Customer segments with actionable insights
- VIP customer identification
- Segment-specific recommendations
- Customer lifetime value insights

### 🛒 **Market Basket Analysis**
- Product association rules (Support, Confidence, Lift)
- Cross-selling opportunities
- Product bundle recommendations
- Frequently bought together insights

### 📈 **Cohort Analysis**
- Customer retention tracking
- Cohort performance heatmaps
- Retention curves by cohort
- Critical drop-off period identification

### 🔮 **Predictive Analytics**
- 12-month sales forecasting
- Seasonal pattern analysis
- Growth projections with confidence intervals
- Month-over-month growth trends

### 💰 **CLV & Churn Prediction**
- Customer lifetime value prediction (ML)
- Churn risk analysis and scoring
- Strategic customer matrix
- High-risk customer identification
- Retention strategy recommendations

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Installation

1. **Clone or download this repository**
```bash
cd retail_dashboard
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Prepare your data**

Place your retail data CSV file in the project root and update the path if needed.

Required columns:
- `InvoiceNo`: Transaction ID
- `StockCode`: Product code
- `Description`: Product description
- `Quantity`: Quantity purchased
- `InvoiceDate`: Transaction date (MM/DD/YYYY HH:MM format)
- `UnitPrice`: Price per unit
- `CustomerID`: Customer ID
- `Country`: Customer country

4. **Run data preparation**
```bash
python prepare_data.py
```

This will:
- Clean and validate data
- Create derived columns
- Generate RFM analysis
- Calculate product/country/monthly metrics

5. **Launch the dashboard**
```bash
streamlit run app.py
```

The dashboard will open in your browser at `http://localhost:8501`

## 📁 Project Structure

```
retail_dashboard/
├── app.py                          # Main entry point
├── requirements.txt                # Python dependencies
├── style.css                       # Custom CSS styling
├── prepare_data.py                 # Data preparation script
├── README.md                       # This file
├── .streamlit/
│   └── config.toml                 # Streamlit configuration
├── data/                           # Data directory
│   ├── retail_data_cleaned.csv    # Cleaned data
│   ├── rfm_analysis.csv           # RFM segments
│   ├── product_metrics.csv        # Product performance
│   ├── country_metrics.csv        # Country performance
│   └── monthly_metrics.csv        # Monthly aggregates
├── pages/                          # Dashboard pages
│   ├── 1_📊_Overview.py
│   ├── 2_👥_Customer_Analysis.py
│   ├── 3_🛒_Basket_Analysis.py
│   ├── 4_📈_Cohort_Analysis.py
│   ├── 5_🔮_Predictive_Analytics.py
│   └── 6_💰_CLV_and_Churn.py
└── utils/                          # Utility modules
    ├── __init__.py
    ├── data_processor.py          # Data processing functions
    ├── ml_models.py               # ML models
    └── theme.py                   # UI components & styling
```

## 🎨 Customization

### Colors & Theme
Edit `utils/theme.py` to customize colors:
```python
class Colors:
    BLUE_ENERGY = "#3A8DFF"    # Primary color
    MINT_LEAF = "#4CC9A6"      # Success color
    # ... add your colors
```

### Styling
Edit `style.css` to customize CSS styles.

### Configuration
Edit `.streamlit/config.toml` for Streamlit settings.

## 📊 Data Requirements

### Minimum Requirements
- At least 1000 transactions
- At least 100 unique customers
- At least 3 months of data
- Valid date formats

### Optimal Performance
- 10,000+ transactions
- 500+ unique customers
- 12+ months of data
- Clean, validated data

## 🔧 Troubleshooting

### Common Issues

**Issue: "Data file not found"**
- Solution: Run `prepare_data.py` first
- Ensure `sample_data.csv` exists in project root or `data/` folder

**Issue: "Module not found"**
- Solution: Install dependencies: `pip install -r requirements.txt`
- Ensure you're in the correct directory

**Issue: Charts not displaying**
- Solution: Clear browser cache and refresh
- Check browser console for errors

**Issue: Slow performance**
- Solution: Reduce dataset size or implement sampling
- Check available RAM

### Getting Help
1. Check error messages carefully
2. Verify data file format and structure
3. Ensure all dependencies are installed
4. Review prepare_data.py output for errors

## 📈 Performance Optimization

For large datasets (100K+ rows):
1. Implement data sampling for analysis
2. Use session state caching
3. Optimize dataframe operations
4. Consider database backend

## 🔒 Security Notes

- Dashboard runs locally by default
- No external API calls (except for ML models)
- Data stays on your machine
- For production deployment, add authentication

## 🚢 Deployment

### Streamlit Cloud
1. Push code to GitHub
2. Connect to Streamlit Cloud
3. Add secrets for sensitive data
4. Deploy with one click

### Docker
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["streamlit", "run", "app.py"]
```

### Heroku
```bash
heroku create your-app-name
git push heroku main
```

## 📝 License

This project is provided as-is for educational and commercial use.

## 🙏 Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Visualizations powered by [Plotly](https://plotly.com/)
- ML models using [scikit-learn](https://scikit-learn.org/)

## 📧 Support

For issues and questions:
1. Check the troubleshooting section
2. Review error logs
3. Verify data format compliance

## 🔄 Updates & Maintenance

### Current Version: 1.0.0

### Changelog
- v1.0.0 (2024-01): Initial release
  - Complete dashboard with 6 analysis modules
  - ML-powered predictions
  - Interactive visualizations
  - Comprehensive documentation

### Future Enhancements
- Real-time data connection
- Advanced ML models (LSTM, Prophet)
- Export to PDF reports
- Email alerts for key metrics
- Multi-user support
- Database integration

---

**Made with ❤️ for Data-Driven Businesses**
