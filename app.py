import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(page_title='Food Price & Inflation Tracker', layout='wide')

st.title('Global Food Price & Inflation Tracker')
st.markdown('''
**Analytical Question:** How do global food price fluctuations transmit to consumer price inflation across major economies?  
**Target User:** Macro investors, policy researchers, and analysts monitoring food-driven inflation.  
**Data Sources:**
- FAO Food Price Index: https://www.fao.org/worldfoodsituation/foodpricesindex/en/
- FAOSTAT Consumer Price Indices: https://www.fao.org/faostat/en/#data/CP
- Both accessed: 19 April 2026
''')

@st.cache_data
def load_data():
    fao_raw = pd.read_csv('food_price_indices_data.csv', skiprows=2)
    fao = fao_raw[['Date', 'Food Price Index', 'Meat', 'Dairy', 'Cereals', 'Oils', 'Sugar']].copy()
    fao = fao.dropna(subset=['Date'])
    fao['Date'] = pd.to_datetime(fao['Date'], format='%Y-%m')
    for col in ['Food Price Index', 'Meat', 'Dairy', 'Cereals', 'Oils', 'Sugar']:
        fao[col] = pd.to_numeric(fao[col], errors='coerce')
    fao = fao[fao['Date'] >= '2000-01-01'].reset_index(drop=True)
    cpi_raw = pd.read_csv('FAOSTAT_data_en_4-19-2026_2.csv')
    month_map = {
        'January':1,'February':2,'March':3,'April':4,
        'May':5,'June':6,'July':7,'August':8,
        'September':9,'October':10,'November':11,'December':12
    }
    country_rename = {
        'China, mainland': 'China',
        'United States of America': 'USA',
        'Russian Federation': 'Russia',
        'United Kingdom of Great Britain and Northern Ireland': 'United Kingdom'
    }
    cpi_general = cpi_raw[cpi_raw['Item'] == 'Consumer Prices, General Indices (2015 = 100)'].copy()
    cpi_general['Month_Num'] = cpi_general['Months'].map(month_map)
    cpi_general['Date'] = pd.to_datetime(
        cpi_general['Year'].astype(str) + '-' + cpi_general['Month_Num'].astype(str), format='%Y-%m'
    )
    cpi_general = cpi_general.rename(columns={'Area': 'Country', 'Value': 'CPI'})
    cpi_general['Country'] = cpi_general['Country'].replace(country_rename)
    cpi_general = cpi_general[['Country', 'Date', 'CPI']].dropna()
    cpi_pivot = cpi_general.pivot_table(index='Date', columns='Country', values='CPI').sort_index()
    return fao, cpi_pivot, cpi_general, cpi_raw, month_map, country_rename

fao, cpi_pivot, cpi_general, cpi_raw, month_map, country_rename = load_data()
latest = fao.iloc[-1]
prev = fao.iloc[-2]

st.subheader('Latest FAO Food Price Index — ' + str(latest['Date'].strftime('%B %Y')))
col1, col2, col3, col4, col5, col6 = st.columns(6)
metrics = [
    ('Food Index', 'Food Price Index'),
    ('Cereals', 'Cereals'),
    ('Oils', 'Oils'),
    ('Meat', 'Meat'),
    ('Dairy', 'Dairy'),
    ('Sugar', 'Sugar')
]
for col, (label, key) in zip([col1, col2, col3, col4, col5, col6], metrics):
    val = latest[key]
    delta = val - prev[key]
    col.metric(label=label, value=f'{val:.1f}', delta=f'{delta:.1f}')

with st.expander('About this dashboard - click to expand'):
    st.markdown('''
    This dashboard explores how global food price fluctuations transmit to consumer price inflation across 14 major economies from 2000 to 2026.
    
    **How to use:**
    - Use the tabs below to explore different analyses
    - In the CPI tab, select countries and drag the year slider to filter
    - In the Lag Analysis tab, select countries to compare transmission speed
    
    **Tabs overview:**
    - **Food Price Overview** — FAO Food Price Index trends with key event markers
    - **CPI by Country** — Interactive CPI comparison
    - **Correlation** — Which countries respond most strongly to global food prices
    - **Lag Analysis** — How many months does price transmission take
    - **Food vs General CPI** — Is food inflation faster than overall inflation
    - **Ukraine War Impact** — How much did CPI rise after the 2022 war
    ''')

col_a, col_b, col_c = st.columns(3)
with col_a:
    st.success('**Food Price Overview** — FAO index trends & sub-indices breakdown')
with col_b:
    st.info('**CPI & Correlation** — Compare 14 countries, lag analysis')
with col_c:
    st.warning('**Deep Analysis** — Food vs General CPI & Ukraine War impact')

st.divider()

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(['Food Price Overview', 'CPI by Country', 'Correlation', 'Lag Analysis', 'Food vs General CPI', 'Ukraine War Impact'])
with tab1:
    st.subheader('FAO Food Price Index (2000-2026)')
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(
        x=fao['Date'], y=fao['Food Price Index'],
        mode='lines', name='Food Price Index',
        line=dict(color='#c0392b', width=2),
        fill='tozeroy', fillcolor='rgba(192,57,43,0.1)'
    ))
    events = {
        '2008-06': '2008 Food Crisis',
        '2011-02': '2011 Arab Spring',
        '2020-04': 'COVID-19',
        '2022-03': 'Ukraine War'
    }
    for date_str, label in events.items():
        fig1.add_vline(x=date_str, line_dash='dash', line_color='gray', opacity=0.6)
        fig1.add_annotation(x=date_str, y=160, text=label, showarrow=False,
                           font=dict(size=10, color='gray'), textangle=-90)
    fig1.update_layout(
        xaxis_title='Date', yaxis_title='Index (2014-2016 = 100)',
        hovermode='x unified', height=400
    )
    st.plotly_chart(fig1, use_container_width=True)

    st.subheader('Sub-indices Breakdown')
    sub_cols = ['Cereals', 'Oils', 'Meat', 'Dairy', 'Sugar']
    fig2 = px.line(fao, x='Date', y=sub_cols, height=400)
    fig2.update_layout(
        xaxis_title='Date', yaxis_title='Index (2014-2016 = 100)',
        hovermode='x unified', legend_title='Category'
    )
    st.plotly_chart(fig2, use_container_width=True)
    st.info('''
    **Key Insights:**
    - Oils showed the most extreme spike in 2022 (above 250), driven by Ukraine War disruptions
    - Cereals and Dairy also surged post-2020, while Meat remained relatively stable
    - Sugar shows the highest short-term volatility across the entire period
    ''')
with tab2:
    st.subheader('CPI Trends by Country')
    all_countries = sorted(list(cpi_pivot.columns))
    selected_countries = st.multiselect(
        'Select countries to compare:',
        options=all_countries,
        default=['USA', 'China', 'Germany', 'India'],
        key='cpi_countries'
    )
    year_range = st.slider(
        'Select year range:',
        min_value=2000,
        max_value=2025,
        value=(2000, 2025),
        key='year_slider'
    )
    if selected_countries:
        filtered = cpi_pivot[selected_countries]
        filtered = filtered[
            (filtered.index.year >= year_range[0]) &
            (filtered.index.year <= year_range[1])
        ]
        filtered_long = filtered.reset_index().melt(
            id_vars='Date', var_name='Country', value_name='CPI'
        )
        fig3 = px.line(
            filtered_long, x='Date', y='CPI', color='Country',
            title='General CPI Comparison', height=500
        )
        fig3.update_layout(
            xaxis_title='Date', yaxis_title='CPI (2015 = 100)',
            hovermode='x unified', legend_title='Country'
        )
        st.plotly_chart(fig3, use_container_width=True)
        st.subheader('Data Table')
        st.dataframe(filtered.round(2))
        st.info('''
        **Key Insights:**
        - Emerging markets show steeper CPI slopes than developed economies
        - All countries experienced a sharp CPI acceleration after 2020
        - China shows relatively low and stable CPI compared to other economies
        ''')
    else:
        st.warning('Please select at least one country.')
with tab3:
    st.subheader('Correlation: FAO Food Price Index vs National CPI')
    fao_change = fao.set_index('Date')[['Food Price Index']].pct_change() * 100
    fao_change.columns = ['FAO_pct']
    cpi_change = cpi_pivot.pct_change() * 100
    merged = fao_change.join(cpi_change, how='inner').dropna()
    countries = [c for c in cpi_pivot.columns if c in merged.columns]
    corr_values = {}
    for country in countries:
        corr = merged['FAO_pct'].corr(merged[country])
        corr_values[country] = round(corr, 3)
    corr_df = pd.DataFrame.from_dict(corr_values, orient='index', columns=['Correlation'])
    corr_df = corr_df.sort_values('Correlation', ascending=False).reset_index()
    corr_df.columns = ['Country', 'Correlation']
    fig4 = px.bar(
        corr_df, x='Country', y='Correlation',
        color='Correlation',
        color_continuous_scale=['#3498db', '#e74c3c'],
        text='Correlation',
        height=450
    )
    fig4.update_traces(texttemplate='%{text:.2f}', textposition='outside')
    fig4.update_layout(
        xaxis_title='Country',
        yaxis_title='Pearson Correlation Coefficient',
        yaxis_range=[-0.15, 0.5],
        coloraxis_showscale=False,
        hovermode='x'
    )
    st.plotly_chart(fig4, use_container_width=True)
    top_country = corr_df.iloc[0]['Country']
    top_val = corr_df.iloc[0]['Correlation']
    bot_country = corr_df.iloc[-1]['Country']
    bot_val = corr_df.iloc[-1]['Correlation']
    st.info(f'''
    **Key Insights:**
    - **Strongest response:** {top_country} (r = {top_val}) — food price changes transmit to CPI most directly
    - **Weakest response:** {bot_country} (r = {bot_val}) — CPI appears largely insulated from global food prices
    - Overall correlations are moderate, reflecting that food is only one component of CPI
    ''')
with tab4:
    st.subheader('Lag Analysis: How Many Months Does Food Price Transmission Take?')
    lag_months = [0, 3, 6, 12]
    lag_results = {}
    for country in countries:
        lag_results[country] = {}
        for lag in lag_months:
            fao_lagged = merged['FAO_pct'].shift(lag)
            corr = fao_lagged.corr(merged[country])
            lag_results[country][f'Lag {lag}m'] = round(corr, 3)
    lag_df = pd.DataFrame(lag_results).T
    selected_lag_countries = st.multiselect(
        'Select countries for lag analysis:',
        options=list(lag_df.index),
        default=['USA', 'Japan', 'Germany'],
        key='lag_countries'
    )
    if selected_lag_countries:
        filtered_lag = lag_df.loc[selected_lag_countries].reset_index()
        filtered_lag.columns = ['Country'] + [f'Lag {l}m' for l in lag_months]
        filtered_lag_long = filtered_lag.melt(
            id_vars='Country', var_name='Lag', value_name='Correlation'
        )
        fig5 = px.bar(
            filtered_lag_long, x='Country', y='Correlation',
            color='Lag', barmode='group',
            color_discrete_sequence=['#2c3e50', '#e74c3c', '#e67e22', '#27ae60'],
            height=450,
            title='Correlation at Different Lag Periods'
        )
        fig5.update_layout(
            xaxis_title='Country',
            yaxis_title='Pearson Correlation',
            hovermode='x unified',
            legend_title='Lag Period'
        )
        st.plotly_chart(fig5, use_container_width=True)
        st.subheader('Lag Data Table')
        st.dataframe(lag_df.loc[selected_lag_countries].round(3))
        best_lag_country = lag_df.apply(lambda x: x.idxmax(), axis=1)
        japan_best = best_lag_country.get('Japan', 'N/A')
        usa_best = best_lag_country.get('USA', 'N/A')
        st.info(f'''
        **Key Insights:**
        - **USA** shows strongest response at {usa_best} — food prices transmit to US CPI quickly
        - **Japan** shows strongest response at {japan_best} — suggesting a longer transmission delay
        - Countries with longer lags may have stronger price controls or import subsidies buffering the shock
        ''')
    else:
        st.warning('Please select at least one country.')
with tab5:
    st.subheader('Food CPI vs General CPI by Country')
    cpi_food = cpi_raw[cpi_raw['Item'] == 'Consumer Prices, Food Indices (2015 = 100)'].copy()
    cpi_food['Month_Num'] = cpi_food['Months'].map(month_map)
    cpi_food['Date'] = pd.to_datetime(
        cpi_food['Year'].astype(str) + '-' + cpi_food['Month_Num'].astype(str), format='%Y-%m'
    )
    cpi_food = cpi_food.rename(columns={'Area': 'Country', 'Value': 'Food_CPI'})
    cpi_food['Country'] = cpi_food['Country'].replace(country_rename)
    cpi_food = cpi_food[['Country', 'Date', 'Food_CPI']].dropna()

    selected_country_tab5 = st.selectbox(
        'Select a country:',
        options=sorted(cpi_general['Country'].unique()),
        key='tab5_country'
    )
    gen = cpi_general[cpi_general['Country'] == selected_country_tab5][['Date', 'CPI']].copy()
    food = cpi_food[cpi_food['Country'] == selected_country_tab5][['Date', 'Food_CPI']].copy()
    combined = pd.merge(gen, food, on='Date')

    fig6 = go.Figure()
    fig6.add_trace(go.Scatter(
        x=combined['Date'], y=combined['CPI'],
        mode='lines', name='General CPI',
        line=dict(color='#3498db', width=2)
    ))
    fig6.add_trace(go.Scatter(
        x=combined['Date'], y=combined['Food_CPI'],
        mode='lines', name='Food CPI',
        line=dict(color='#e74c3c', width=2)
    ))
    fig6.update_layout(
        title=f'Food CPI vs General CPI — {selected_country_tab5}',
        xaxis_title='Date',
        yaxis_title='CPI (2015 = 100)',
        hovermode='x unified',
        height=450,
        legend_title='Type'
    )
    st.plotly_chart(fig6, use_container_width=True)

    combined['Gap'] = combined['Food_CPI'] - combined['CPI']
    fig7 = px.area(
        combined, x='Date', y='Gap',
        title=f'Food CPI minus General CPI — {selected_country_tab5}',
        height=350,
        color_discrete_sequence=['#e67e22']
    )
    fig7.update_layout(
        xaxis_title='Date',
        yaxis_title='Difference',
        hovermode='x unified'
    )
    st.plotly_chart(fig7, use_container_width=True)
    avg_gap = combined['Gap'].mean()
    max_gap_date = combined.loc[combined['Gap'].idxmax(), 'Date'].strftime('%Y-%m')
    st.info(f'''
    **Key Insights:**
    - Average gap between Food CPI and General CPI for {selected_country_tab5}: {avg_gap:.1f} points
    - Largest divergence occurred around {max_gap_date}
    - Positive values mean food prices are rising faster than general inflation
    ''')
with tab6:
    st.subheader('Ukraine War Impact — Food Price Shock Analysis')
    st.markdown('Comparing FAO Food Price Index and national CPI **12 months before and after** the Ukraine War (March 2022)')

    war_date = pd.to_datetime('2022-03-01')
    pre_start = pd.to_datetime('2021-03-01')
    post_end = pd.to_datetime('2023-03-01')

    fao_war = fao[(fao['Date'] >= pre_start) & (fao['Date'] <= post_end)][['Date', 'Food Price Index']].copy()
    fao_war['Period'] = fao_war['Date'].apply(lambda x: 'Before War' if x < war_date else 'After War')

    fig8 = px.line(
        fao_war, x='Date', y='Food Price Index',
        color='Period',
        color_discrete_map={'Before War': '#3498db', 'After War': '#e74c3c'},
        title='FAO Food Price Index: Before vs After Ukraine War',
        height=400
    )
    fig8.add_vline(x='2022-03-01', line_dash='dash', line_color='black')
    fig8.add_annotation(x='2022-03-01', y=160, text='War Starts', showarrow=False,
                       font=dict(size=11, color='black'))
    fig8.update_layout(hovermode='x unified', xaxis_title='Date', yaxis_title='Index (2014-2016 = 100)')
    st.plotly_chart(fig8, use_container_width=True)

    st.subheader('CPI Change by Country After Ukraine War')
    war_impact = {}
    for country in cpi_pivot.columns:
        pre = cpi_pivot.loc[(cpi_pivot.index >= pre_start) & (cpi_pivot.index < war_date), country].mean()
        post = cpi_pivot.loc[(cpi_pivot.index >= war_date) & (cpi_pivot.index <= post_end), country].mean()
        if pd.notna(pre) and pd.notna(post) and pre != 0:
            war_impact[country] = round(((post - pre) / pre) * 100, 2)

    impact_df = pd.DataFrame.from_dict(war_impact, orient='index', columns=['CPI Change (%)'])
    impact_df = impact_df.sort_values('CPI Change (%)', ascending=False).reset_index()
    impact_df.columns = ['Country', 'CPI Change (%)']

    fig9 = px.bar(
        impact_df, x='Country', y='CPI Change (%)',
        color='CPI Change (%)',
        color_continuous_scale=['#3498db', '#e74c3c'],
        text='CPI Change (%)',
        title='Average CPI Change After Ukraine War by Country',
        height=450
    )
    fig9.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    fig9.update_layout(
        xaxis_title='Country',
        yaxis_title='CPI Change (%)',
        coloraxis_showscale=False,
        hovermode='x'
    )
    st.plotly_chart(fig9, use_container_width=True)

    top_war = impact_df.iloc[0]['Country']
    top_war_val = impact_df.iloc[0]['CPI Change (%)']
    bot_war = impact_df.iloc[-1]['Country']
    bot_war_val = impact_df.iloc[-1]['CPI Change (%)']
    st.info(f'''
    **Key Insights:**
    - **Most affected:** {top_war} (+{top_war_val}%) — largest CPI increase after the war began
    - **Least affected:** {bot_war} (+{bot_war_val}%) — most insulated from the war shock
    - The war caused widespread inflation across all 14 economies, but with varying intensity
    ''')