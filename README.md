# Global Food Price & Inflation Tracker

## Live Demo
👉 https://acc102-food-inflation-tracker-csd5ekukjwdopipfzj5iec.streamlit.app/

## 1. Problem & User
This tool investigates how global food price fluctuations transmit to consumer price inflation across 14 major economies. The intended users are macro investors, policy researchers, and analysts who need to monitor and anticipate food-driven inflation trends.

## 2. Data
| Dataset | Source | Access Date | Key Fields |
|---------|--------|-------------|------------|
| FAO Food Price Index | https://www.fao.org/worldfoodsituation/foodpricesindex/en/ | 19 April 2026 | Food, Cereals, Oils, Meat, Dairy, Sugar |
| FAOSTAT Consumer Price Indices | https://www.fao.org/faostat/en/#data/CP | 19 April 2026 | General CPI, Food CPI, 14 countries, 2000–2025 |

## 3. Methods
- Data cleaning: parsed date strings, mapped month names to numbers, standardised country names using pandas
- Correlation analysis: calculated Pearson correlation between month-on-month % changes of FAO index and national CPI
- Lag analysis: shifted FAO index by 0, 3, 6, and 12 months to identify transmission delay per country
- Event analysis: compared average CPI 12 months before and after the Ukraine War (March 2022)
- Visualisation: interactive charts built with Plotly, deployed via Streamlit

## 4. Key Findings
- USA shows the strongest immediate correlation with global food prices (r = 0.314)
- Japan's strongest correlation appears at a 6-month lag, suggesting delayed transmission
- United Kingdom and Indonesia show highest correlation at 12-month lag
- Russia experienced the largest CPI increase after the Ukraine War (+14.29%)
- China was the least affected by the Ukraine War shock (+2.06%)

## 5. How to Run
```bash
git clone https://github.com/Wozhenshipofang/acc102-food-inflation-tracker
cd acc102-food-inflation-tracker
pip install -r requirements.txt
streamlit run app.py
```

## 6. Product Link / Demo
- Live app: https://acc102-food-inflation-tracker-csd5ekukjwdopipfzj5iec.streamlit.app/
- Notebook: acc102-food-inflation.ipynb

## 7. Limitations & Next Steps
- Correlations are moderate overall as food is only one component of CPI
- Analysis does not control for confounding variables such as exchange rates or energy prices
- Future work could extend to more countries and incorporate regression modelling
