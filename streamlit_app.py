"""
Car Price Prediction - Streamlit Dashboard
============================================
Interactive dashboard for exploring the car price dataset,
comparing ML models, and predicting car prices.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import joblib
import os
import warnings
warnings.filterwarnings('ignore')

# =========================================================================
# Page Config
# =========================================================================
st.set_page_config(
    page_title="Car Price Explorer",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================================
# Cache Loading Functions
# =========================================================================
@st.cache_data
def load_data():
    df = pd.read_csv('Cleaned_Car_data.csv', index_col=0)
    df['car_age'] = 2025 - df['year']
    return df

@st.cache_resource
def load_preprocessor():
    return joblib.load('ml_ready/preprocessor.pkl')

@st.cache_resource
def load_models():
    models = {}
    model_dir = 'ml_ready/models'
    for fname in os.listdir(model_dir):
        if fname.endswith('.pkl'):
            name = fname.replace('.pkl', '').replace('_', ' ').title()
            models[name] = joblib.load(os.path.join(model_dir, fname))
    return models

# =========================================================================
# Load Data
# =========================================================================
df = load_data()
preprocessor = load_preprocessor()
models = load_models()

# Compute summary stats
fuel_types = sorted(df['fuel_type'].unique())
companies = sorted(df['company'].unique())
COMPANY_COUNT = len(companies)
FUEL_COLORS = {
    'Diesel': '#2E86AB', 'Petrol': '#A23B72', 'CNG': '#F18F01',
    'LPG': '#C73E1D', 'Electric': '#6A994E'
}

# =========================================================================
# Sidebar
# =========================================================================
st.sidebar.title("🚗 Car Price Explorer")
st.sidebar.markdown("---")
st.sidebar.markdown("### Navigation")

page = st.sidebar.radio(
    "Go to",
    ["📊 Dataset Explorer", "📈 EDA Visualizations", "🤖 Model Comparison", "🔮 Price Predictor"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### Dataset Summary")
st.sidebar.metric("Total Cars", f"{len(df):,}")
st.sidebar.metric("Companies", COMPANY_COUNT)
st.sidebar.metric("Price Range", f"₹{df['Price'].min():,.0f} - ₹{df['Price'].max():,.0f}")
st.sidebar.metric("Avg Price", f"₹{df['Price'].mean():,.0f}")

# =========================================================================
# PAGE 1: Dataset Explorer
# =========================================================================
if page == "📊 Dataset Explorer":
    st.title("📊 Dataset Explorer")
    st.markdown("Explore the car price dataset with interactive filters.")

    # Filters
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        selected_companies = st.multiselect(
            "Company", companies, default=companies[:10],
            placeholder="Select companies..."
        )
    with col2:
        selected_fuels = st.multiselect(
            "Fuel Type", fuel_types, default=fuel_types,
            placeholder="Select fuel types..."
        )
    with col3:
        year_range = st.slider(
            "Year Range",
            int(df['year'].min()), int(df['year'].max()),
            (int(df['year'].min()), int(df['year'].max()))
        )
    with col4:
        price_range = st.slider(
            "Price Range (₹)",
            float(df['Price'].min()), float(df['Price'].max()),
            (float(df['Price'].min()), float(df['Price'].max())),
            format="₹%.0f"
        )

    # Filter
    mask = (
        df['company'].isin(selected_companies) &
        df['fuel_type'].isin(selected_fuels) &
        df['year'].between(year_range[0], year_range[1]) &
        df['Price'].between(price_range[0], price_range[1])
    )
    filtered = df[mask].copy()

    st.markdown(f"### Showing {len(filtered):,} of {len(df):,} cars")

    # Tabs within the page
    tab1, tab2, tab3 = st.tabs(["📋 Data Table", "📊 Distributions", "📈 Price Trends"])

    with tab1:
        col_config = {
            'name': st.column_config.TextColumn("Car Name"),
            'company': st.column_config.TextColumn("Company"),
            'year': st.column_config.NumberColumn("Year", format="%d"),
            'Price': st.column_config.NumberColumn("Price (₹)", format="₹%d"),
            'kms_driven': st.column_config.NumberColumn("KMs Driven", format="%d"),
            'fuel_type': st.column_config.TextColumn("Fuel Type"),
            'car_age': st.column_config.NumberColumn("Age (yrs)", format="%d")
        }
        st.dataframe(
            filtered.sort_values('Price', ascending=False)
            .reset_index(drop=True),
            column_config=col_config,
            use_container_width=True,
            height=500
        )

    with tab2:
        col_a, col_b = st.columns(2)

        with col_a:
            # Price distribution
            fig = px.histogram(
                filtered, x='Price', nbins=50,
                color_discrete_sequence=['#2E86AB'],
                marginal='box', title='Price Distribution'
            )
            fig.update_layout(height=350, showlegend=False)
            fig.update_xaxes(title="Price (₹)")
            st.plotly_chart(fig, use_container_width=True)

            # Fuel type breakdown
            fuel_counts = filtered['fuel_type'].value_counts().reset_index()
            fuel_counts.columns = ['Fuel Type', 'Count']
            fig2 = px.pie(
                fuel_counts, values='Count', names='Fuel Type',
                color='Fuel Type', color_discrete_map=FUEL_COLORS,
                title='Fuel Type Breakdown'
            )
            fig2.update_layout(height=300)
            st.plotly_chart(fig2, use_container_width=True)

        with col_b:
            # KMs distribution
            fig3 = px.histogram(
                filtered, x='kms_driven', nbins=50,
                color_discrete_sequence=['#A23B72'],
                marginal='box', title='KMs Driven Distribution'
            )
            fig3.update_layout(height=350, showlegend=False)
            fig3.update_xaxes(title="Kilometers Driven")
            st.plotly_chart(fig3, use_container_width=True)

            # Year distribution
            year_counts = filtered['year'].value_counts().sort_index().reset_index()
            year_counts.columns = ['Year', 'Count']
            fig4 = px.bar(
                year_counts, x='Year', y='Count',
                color_discrete_sequence=['#F18F01'],
                title='Cars by Manufacturing Year'
            )
            fig4.update_layout(height=300)
            st.plotly_chart(fig4, use_container_width=True)

    with tab3:
        col_c, col_d = st.columns(2)

        with col_c:
            # Avg price by company
            avg_price = filtered.groupby('company')['Price'].mean().sort_values(ascending=False).reset_index()
            fig5 = px.bar(
                avg_price.head(15), x='Price', y='company',
                orientation='h', color='Price',
                color_continuous_scale='Viridis',
                title='Average Price by Company (Top 15)'
            )
            fig5.update_layout(height=400, yaxis={'categoryorder': 'total ascending'})
            fig5.update_xaxes(title="Avg Price (₹)")
            fig5.update_yaxes(title="")
            st.plotly_chart(fig5, use_container_width=True)

        with col_d:
            # Price vs Age scatter
            fig6 = px.scatter(
                filtered, x='car_age', y='Price',
                color='fuel_type', color_discrete_map=FUEL_COLORS,
                hover_data=['name', 'company', 'kms_driven'],
                size='kms_driven', size_max=15,
                title='Price vs Car Age (bubble size = KMs driven)',
                opacity=0.6
            )
            fig6.update_layout(height=400)
            fig6.update_xaxes(title="Car Age (years)")
            fig6.update_yaxes(title="Price (₹)")
            st.plotly_chart(fig6, use_container_width=True)

# =========================================================================
# PAGE 2: EDA Visualizations
# =========================================================================
elif page == "📈 EDA Visualizations":
    st.title("📈 EDA Visualizations")
    st.markdown("Interactive exploratory data analysis charts.")

    viz_option = st.radio(
        "Select Visualization",
        [
            "Price Distribution", "Price by Fuel Type", "Company Price Comparison",
            "Price vs Age", "KMs & Year Analysis", "Correlation Heatmap", "Top 10 Most Expensive"
        ],
        horizontal=True
    )

    if viz_option == "Price Distribution":
        col1, col2 = st.columns(2)
        with col1:
            fig = px.histogram(
                df, x='Price', nbins=60, color_discrete_sequence=['#2E86AB'],
                marginal='box', title='Distribution of Car Prices'
            )
            fig.update_layout(height=450)
            fig.update_xaxes(title="Price (₹)")
            st.plotly_chart(fig, use_container_width=True)

            stats = df['Price'].describe()
            st.markdown("### Price Statistics")
            stat_cols = st.columns(5)
            metrics = [
                ("Min", f"₹{stats['min']:,.0f}"),
                ("Median", f"₹{stats['50%']:,.0f}"),
                ("Mean", f"₹{stats['mean']:,.0f}"),
                ("Max", f"₹{stats['max']:,.0f}"),
                ("Std Dev", f"₹{stats['std']:,.0f}")
            ]
            for col, (label, val) in zip(stat_cols, metrics):
                col.metric(label, val)

        with col2:
            log_prices = np.log1p(df['Price'])
            fig2 = px.histogram(
                x=log_prices, nbins=60, color_discrete_sequence=['#A23B72'],
                marginal='box', title='Log-Transformed Price Distribution'
            )
            fig2.update_layout(height=450)
            fig2.update_xaxes(title="log(Price + 1)")
            st.plotly_chart(fig2, use_container_width=True)

    elif viz_option == "Price by Fuel Type":
        col1, col2 = st.columns(2)
        with col1:
            fig = px.box(
                df, x='fuel_type', y='Price', color='fuel_type',
                color_discrete_map=FUEL_COLORS,
                title='Price Distribution by Fuel Type',
                points='outliers'
            )
            fig.update_layout(height=450)
            fig.update_xaxes(title="Fuel Type")
            fig.update_yaxes(title="Price (₹)")
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig2 = px.violin(
                df, x='fuel_type', y='Price', color='fuel_type',
                color_discrete_map=FUEL_COLORS,
                box=True, title='Violin Plot: Price by Fuel Type'
            )
            fig2.update_layout(height=450)
            fig2.update_xaxes(title="Fuel Type")
            fig2.update_yaxes(title="Price (₹)")
            st.plotly_chart(fig2, use_container_width=True)

        st.markdown("### Average Price by Fuel Type")
        fuel_stats = df.groupby('fuel_type')['Price'].agg(['mean', 'median', 'count', 'std']).round(0)
        fuel_stats.columns = ['Mean Price', 'Median Price', 'Count', 'Std Dev']
        fuel_stats['Mean Price'] = fuel_stats['Mean Price'].apply(lambda x: f'₹{x:,.0f}')
        fuel_stats['Median Price'] = fuel_stats['Median Price'].apply(lambda x: f'₹{x:,.0f}')
        fuel_stats['Std Dev'] = fuel_stats['Std Dev'].apply(lambda x: f'₹{x:,.0f}')
        st.dataframe(fuel_stats, use_container_width=True)

    elif viz_option == "Company Price Comparison":
        top_n = st.slider("Number of companies", 5, COMPANY_COUNT, 20)

        col1, col2 = st.columns(2)
        with col1:
            avg_prices = df.groupby('company')['Price'].mean().sort_values(ascending=False).head(top_n).reset_index()
            fig = px.bar(
                avg_prices, x='Price', y='company',
                color='Price', color_continuous_scale='Viridis',
                orientation='h', title=f'Top {top_n} Companies by Average Price'
            )
            fig.update_layout(height=500)
            fig.update_yaxes(title="", categoryorder='total ascending')
            fig.update_xaxes(title="Average Price (₹)")
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            top_companies = avg_prices['company'].tolist()
            df_top = df[df['company'].isin(top_companies)]
            fig2 = px.box(
                df_top, x='company', y='Price',
                color='company', title=f'Price Distribution: Top {top_n} Companies',
                points='outliers'
            )
            fig2.update_layout(height=500, showlegend=False)
            fig2.update_xaxes(title="Company", tickangle=-45)
            fig2.update_yaxes(title="Price (₹)")
            st.plotly_chart(fig2, use_container_width=True)

    elif viz_option == "Price vs Age":
        col1, col2 = st.columns(2)
        with col1:
            fig = px.scatter(
                df, x='car_age', y='Price',
                color='fuel_type', color_discrete_map=FUEL_COLORS,
                hover_data=['name', 'company', 'kms_driven', 'year'],
                title='Price vs Car Age (colored by fuel type)',
                opacity=0.5
            )
            fig.update_layout(height=500)
            fig.update_xaxes(title="Car Age (years)")
            fig.update_yaxes(title="Price (₹)")
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig2 = px.scatter(
                df, x='car_age', y='Price',
                color='company',
                hover_data=['name', 'fuel_type', 'kms_driven'],
                title='Price vs Car Age (colored by company)',
                opacity=0.5
            )
            fig2.update_layout(height=500)
            fig2.update_xaxes(title="Car Age (years)")
            fig2.update_yaxes(title="Price (₹)")
            st.plotly_chart(fig2, use_container_width=True)

    elif viz_option == "KMs & Year Analysis":
        col1, col2 = st.columns(2)
        with col1:
            fig = px.histogram(
                df, x='kms_driven', nbins=50,
                color_discrete_sequence=['#6A994E'],
                marginal='box', title='Distribution of Kilometers Driven'
            )
            fig.update_layout(height=400)
            fig.update_xaxes(title="Kilometers Driven")
            st.plotly_chart(fig, use_container_width=True)

            fig2 = px.scatter(
                df, x='kms_driven', y='Price',
                color='car_age', color_continuous_scale='RdYlGn_r',
                hover_data=['name', 'company', 'year'],
                title='Price vs KMs Driven (colored by age)',
                opacity=0.5
            )
            fig2.update_layout(height=400)
            fig2.update_xaxes(title="Kilometers Driven")
            fig2.update_yaxes(title="Price (₹)")
            st.plotly_chart(fig2, use_container_width=True)

        with col2:
            year_counts = df['year'].value_counts().sort_index().reset_index()
            year_counts.columns = ['Year', 'Count']
            fig3 = px.bar(
                year_counts, x='Year', y='Count',
                color='Count', color_continuous_scale='Blues',
                title='Number of Cars by Manufacturing Year'
            )
            fig3.update_layout(height=400)
            st.plotly_chart(fig3, use_container_width=True)

            fig4 = px.scatter(
                df, x='year', y='Price',
                color='kms_driven', color_continuous_scale='RdYlGn_r',
                hover_data=['name', 'company', 'fuel_type'],
                title='Price vs Year (colored by KMs driven)',
                opacity=0.5
            )
            fig4.update_layout(height=400)
            fig4.update_xaxes(title="Manufacturing Year")
            fig4.update_yaxes(title="Price (₹)")
            st.plotly_chart(fig4, use_container_width=True)

    elif viz_option == "Correlation Heatmap":
        num_cols = ['Price', 'year', 'kms_driven', 'car_age']
        corr = df[num_cols].corr()

        fig = go.Figure(data=go.Heatmap(
            z=corr.values,
            x=corr.columns,
            y=corr.columns,
            text=np.round(corr.values, 3),
            texttemplate='%{text}',
            textfont={"size": 14, "color": "black"},
            colorscale='RdBu_r',
            zmin=-1, zmax=1,
        ))
        fig.update_layout(
            title='Correlation Matrix of Numerical Features',
            height=500,
            width=600
        )
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("### Key Observations")
        st.markdown("""
        - **Price vs car_age**: Strong negative correlation — older cars are cheaper
        - **Price vs year**: Strong positive correlation — newer cars are more expensive
        - **Price vs kms_driven**: Moderate negative correlation — more driven = less valuable
        - **year vs car_age**: Perfect negative correlation (as expected, since car_age = 2025 - year)
        """)

    elif viz_option == "Top 10 Most Expensive":
        top10 = df.nlargest(10, 'Price')[['name', 'company', 'year', 'Price', 'kms_driven', 'fuel_type']]
        top10['Price'] = top10['Price'].apply(lambda x: f'₹{x:,.0f}')
        top10['kms_driven'] = top10['kms_driven'].apply(lambda x: f'{x:,} km')
        top10.index = range(1, 11)

        st.markdown("### Top 10 Most Expensive Cars")
        st.dataframe(top10, use_container_width=True)

        fig = px.bar(
            top10.reset_index(), x='Price', y='name',
            color='company', orientation='h',
            title='Top 10 Most Expensive Cars',
            hover_data=['year', 'fuel_type', 'kms_driven']
        )
        fig.update_layout(height=450, yaxis={'categoryorder': 'total ascending'})
        fig.update_xaxes(title="Price")
        fig.update_yaxes(title="")
        # Clean price strings for display
        fig.update_xaxes(tickprefix="₹")
        st.plotly_chart(fig, use_container_width=True)

# =========================================================================
# PAGE 3: Model Comparison
# =========================================================================
elif page == "🤖 Model Comparison":
    st.title("🤖 Model Performance Comparison")
    st.markdown("Compare how different ML algorithms perform on the car price dataset.")

    # Pre-computed metrics from notebook execution (avoids retraining)
    # Note: Metrics are in ORIGINAL INR scale (log1p-transformed training, expm1-inverted)
    MODEL_METRICS = [
        {'Model': 'Linear Regression', 'Train R²': 0.6797, 'Test R²': 0.7654, 'RMSE': 247535, 'MAE': 136979, 'Time (s)': 0.04},
        {'Model': 'Ridge',             'Train R²': 0.6740, 'Test R²': 0.7605, 'RMSE': 250108, 'MAE': 136875, 'Time (s)': 0.02},
        {'Model': 'XGBoost',           'Train R²': 0.7546, 'Test R²': 0.7463, 'RMSE': 257436, 'MAE': 131764, 'Time (s)': 0.84},
        {'Model': 'Gradient Boosting', 'Train R²': 0.7642, 'Test R²': 0.7373, 'RMSE': 261980, 'MAE': 132826, 'Time (s)': 3.74},
        {'Model': 'SVR',               'Train R²': 0.7910, 'Test R²': 0.6998, 'RMSE': 280045, 'MAE': 137355, 'Time (s)': 26.32},
        {'Model': 'Lasso',             'Train R²': 0.6059, 'Test R²': 0.6585, 'RMSE': 298705, 'MAE': 145382, 'Time (s)': 0.06},
        {'Model': 'KNN',               'Train R²': 0.9556, 'Test R²': 0.6519, 'RMSE': 301578, 'MAE': 150841, 'Time (s)': 0.00},
        {'Model': 'Random Forest',     'Train R²': 0.6363, 'Test R²': 0.5850, 'RMSE': 329250, 'MAE': 147945, 'Time (s)': 1.77},
    ]

    results_df = pd.DataFrame(MODEL_METRICS).sort_values('Test R²', ascending=False).reset_index(drop=True)

    # Metrics Table
    st.markdown("### Performance Metrics")
    display_df = results_df.copy()
    display_df.index = display_df.index + 1
    display_df['Train R²'] = display_df['Train R²'].apply(lambda x: f'{x:.4f}')
    display_df['Test R²'] = display_df['Test R²'].apply(lambda x: f'{x:.4f}')
    display_df['RMSE'] = display_df['RMSE'].apply(lambda x: f'₹{x:,}')
    display_df['MAE'] = display_df['MAE'].apply(lambda x: f'₹{x:,}')

    st.dataframe(display_df, use_container_width=True)

    # Highlight best
    best_row = results_df.loc[results_df['Test R²'].idxmax()]
    st.success(f"**Best Model:** {best_row['Model']} — Test R²: {best_row['Test R²']:.4f}, RMSE: ₹{best_row['RMSE']:,}, MAE: ₹{best_row['MAE']:,}")

    # Charts
    col1, col2 = st.columns(2)
    with col1:
        # R² bar chart
        fig = px.bar(
            results_df.sort_values('Test R²'),
            x='Test R²', y='Model', orientation='h',
            color='Test R²', color_continuous_scale='Viridis',
            title='Test R² Score (higher is better)',
            text='Test R²'
        )
        fig.update_traces(texttemplate='%{text:.4f}', textposition='outside')
        fig.update_layout(height=400, xaxis_range=[0, 1])
        fig.update_yaxes(title="")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # RMSE & MAE grouped bar
        metrics_melted = results_df.melt(
            id_vars=['Model'], value_vars=['RMSE', 'MAE'],
            var_name='Metric', value_name='Value'
        )
        fig2 = px.bar(
            metrics_melted, x='Model', y='Value', color='Metric',
            barmode='group', title='RMSE & MAE Comparison (lower is better)',
            color_discrete_sequence=['#E74C3C', '#3498DB']
        )
        fig2.update_layout(height=400, xaxis_tickangle=-45)
        fig2.update_yaxes(title="Price (₹)")
        st.plotly_chart(fig2, use_container_width=True)

    # Radar chart image
    st.markdown("### Radar Chart — Multi-dimensional Comparison")
    radar_path = os.path.join(os.path.dirname(__file__), 'report_output', 'images', 'radar_comparison.png')
    if os.path.exists(radar_path):
        st.image(radar_path, caption='ML Algorithm Comparison — Radar Chart', use_container_width=True)
    else:
        st.info("Radar chart image not found. Re-run the notebook to generate it.")

# =========================================================================
# PAGE 4: Price Predictor
# =========================================================================
elif page == "🔮 Price Predictor":
    st.title("🔮 Car Price Predictor")
    st.markdown("Enter car details and get an estimated price from ML models.")

    # Input form
    with st.form("prediction_form"):
        st.markdown("### Car Details")
        col1, col2, col3 = st.columns(3)

        with col1:
            company = st.selectbox(
                "Company",
                companies,
                index=companies.index('Maruti') if 'Maruti' in companies else 0,
                help="Car brand/manufacturer"
            )

        with col2:
            fuel_type = st.selectbox(
                "Fuel Type",
                fuel_types,
                index=0,
                help="Type of fuel the car uses"
            )

        with col3:
            year = st.number_input(
                "Manufacturing Year",
                min_value=int(df['year'].min()),
                max_value=2025,
                value=2018,
                help="Year the car was manufactured"
            )

        col4, col5 = st.columns(2)
        with col4:
            kms_driven = st.number_input(
                "Kilometers Driven",
                min_value=0,
                max_value=1000000,
                value=50000,
                step=1000,
                format="%d",
                help="Total distance driven"
            )

        with col5:
            model_choice = st.selectbox(
                "ML Model",
                list(models.keys()),
                index=0,
                help="Which model to use for prediction"
            )

        submitted = st.form_submit_button("🚀 Predict Price", use_container_width=True)

    if submitted:
        with st.spinner("Predicting..."):
            # Build input dataframe matching preprocessor expectations
            car_age = 2025 - year
            fuel_simple = 'Alternative' if fuel_type in ['CNG', 'LPG', 'Electric'] else fuel_type

            input_df = pd.DataFrame([{
                'car_age': car_age,
                'kms_driven': kms_driven,
                'company': company,
                'fuel_type_simple': fuel_simple
            }])

            # Transform
            X_input = preprocessor.transform(input_df)

            # Predict (model predicts in log-space, invert to INR)
            model = models[model_choice]
            pred_log = model.predict(X_input)[0]
            pred = np.expm1(pred_log)  # Convert from log-space back to INR

            # Show result
            st.markdown("## 📊 Prediction Result")
            st.balloons()

            # Look up model metrics (all in original INR scale)
            model_metrics = {
                'Gradient Boosting': {'Test R²': 0.7373, 'RMSE': 261980},
                'XGBoost':           {'Test R²': 0.7463, 'RMSE': 257436},
                'Random Forest':     {'Test R²': 0.6322, 'RMSE': 309960},
                'Linear Regression': {'Test R²': 0.7654, 'RMSE': 247535},
                'Ridge':             {'Test R²': 0.7605, 'RMSE': 250108},
                'Lasso':             {'Test R²': 0.6585, 'RMSE': 298705},
                'SVR':               {'Test R²': 0.6998, 'RMSE': 280045},
                'KNN':               {'Test R²': 0.6519, 'RMSE': 301578},
            }
            meta = model_metrics.get(model_choice, {'Test R²': 0.66, 'RMSE': 300000})

            result_col1, result_col2, result_col3 = st.columns(3)
            with result_col1:
                st.metric("Predicted Price", f"₹{pred:,.0f}")
            with result_col2:
                st.metric("Model", model_choice)
            with result_col3:
                st.metric("Model R² Score", f"{meta['Test R²']:.4f}")

            # Confidence range using model RMSE
            rmse = meta['RMSE']
            st.markdown(f"**Estimated Price Range:** ₹{pred - rmse:,.0f} – ₹{pred + rmse:,.0f} (based on model RMSE of ₹{rmse:,})")

            # Car details summary
            st.markdown("### Input Summary")
            detail_cols = st.columns(5)
            detail_data = [
                ("Company", company),
                ("Fuel", fuel_type),
                ("Year", str(year)),
                ("Age", f"{car_age} yrs"),
                ("KMs", f"{kms_driven:,} km")
            ]
            for col, (label, val) in zip(detail_cols, detail_data):
                col.metric(label, val)

            # Show similar cars from dataset
            st.markdown("### Similar Cars in Dataset")
            similar = df[
                (df['company'] == company) &
                (df['fuel_type'] == fuel_type) &
                (df['car_age'].between(car_age - 2, car_age + 2))
            ].copy()

            if len(similar) > 0:
                similar['Price'] = similar['Price'].apply(lambda x: f'₹{x:,}')
                st.dataframe(
                    similar[['name', 'year', 'Price', 'kms_driven']]
                    .head(10)
                    .reset_index(drop=True),
                    use_container_width=True
                )
            else:
                st.info("No directly similar cars found in the dataset with these exact criteria.")
