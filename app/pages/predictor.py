"""AutoIntel — Price Predictor."""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from app.chart_utils import show_chart
from app.helpers import (
    METRICS_DF,
    MODEL_METRICS,
    compute_deal_score,
    ensemble_prediction,
    fmt_inr,
    generate_natural_language_explanation,
    get_car_name_options,
    get_fuel_simple,
    get_price_tier,
    make_prediction,
    shap_lite_approximation,
)


def page_price_predictor() -> None:
    st.markdown("## 🔮 Price Predictor")
    st.markdown(
        '<p style="color:#8892a0">Get instant price estimates with explainability</p>',
        unsafe_allow_html=True,
    )

    # Track visit
    st.session_state.page_visits["predictor"] = st.session_state.page_visits.get("predictor", 0) + 1

    # AB Mode Toggle
    ab_mode = st.checkbox("🔄 A/B Comparison Mode — Compare Two Cars", key="ab_toggle")
    st.session_state.ab_mode = ab_mode

    num_cars = 2 if ab_mode else 1

    for car_idx in range(num_cars):
        suffix = f"_{car_idx}" if ab_mode else ""
        label = (
            f"### {'🚗 Car A' if car_idx == 0 else '🚙 Car B'}" if ab_mode else "### Car Details"
        )

        with st.container():
            st.markdown(label)
            col1, col2 = st.columns(2)

            with col1:
                company = st.selectbox(
                    "Company",
                    companies,
                    key=f"comp{suffix}",
                    index=(
                        companies.index(
                            st.session_state.last_pred_inputs.get(f"comp{suffix}", "Maruti")
                        )
                        if st.session_state.last_pred_inputs.get(f"comp{suffix}") in companies
                        else 0
                    ),
                )
                get_car_name_options(df, company)
                st.text_input(
                    "Car Name (optional)",
                    key=f"name{suffix}",
                    placeholder="e.g., Swift Dzire VDI",
                )
                year = st.slider(
                    "Year",
                    1996,
                    2024,
                    st.session_state.last_pred_inputs.get(f"year{suffix}", 2018),
                    key=f"year{suffix}",
                )
                fuel = st.selectbox(
                    "Fuel Type",
                    fuel_types,
                    key=f"fuel{suffix}",
                    index=(
                        fuel_types.index(
                            st.session_state.last_pred_inputs.get(f"fuel{suffix}", fuel_types[0])
                        )
                        if st.session_state.last_pred_inputs.get(f"fuel{suffix}") in fuel_types
                        else 0
                    ),
                )

            with col2:
                kms = st.number_input(
                    "KMs Driven",
                    0,
                    500000,
                    st.session_state.last_pred_inputs.get(f"kms{suffix}", 50000),
                    step=1000,
                    key=f"kms{suffix}",
                )
                model_choice = st.selectbox(
                    "ML Model",
                    list(models.keys()),
                    key=f"model{suffix}",
                    index=(
                        list(models.keys()).index(
                            st.session_state.last_pred_inputs.get(
                                f"model{suffix}", next(iter(models.keys()))
                            )
                        )
                        if st.session_state.last_pred_inputs.get(f"model{suffix}") in models
                        else 0
                    ),
                )
                with st.expander("⚙️ Advanced Options"):
                    ci = st.select_slider(
                        "Confidence Interval",
                        options=["±10%", "±15%", "±20%"],
                        value="±15%",
                        key=f"ci{suffix}",
                    )
                    st.checkbox("Show similar cars", value=True, key=f"sim{suffix}")
                    compare_all = st.checkbox("Compare all models", value=False, key=f"all{suffix}")

            # Validation
            car_age = CURRENT_YEAR - year
            warnings_list = []
            if kms < 1000 and car_age > 10:
                warnings_list.append(
                    "⚠️ Suspiciously low mileage for an older car — verify KMs driven"
                )
            if kms > 50000 and car_age < 3:
                warnings_list.append("⚠️ High mileage for a relatively new car — verify")
            if fuel == "Electric" and year < 2015:
                warnings_list.append("⚠️ Electric cars before 2015 are rare — verify fuel type")

            for w in warnings_list:
                st.warning(w)

            st.session_state.last_pred_inputs[f"comp{suffix}"] = company
            st.session_state.last_pred_inputs[f"year{suffix}"] = year
            st.session_state.last_pred_inputs[f"fuel{suffix}"] = fuel
            st.session_state.last_pred_inputs[f"kms{suffix}"] = kms
            st.session_state.last_pred_inputs[f"model{suffix}"] = model_choice

    if st.button("🚀 Predict Price", use_container_width=True, key="predict_btn"):
        for car_idx in range(num_cars):
            suffix = f"_{car_idx}" if ab_mode else ""
            company = st.session_state.last_pred_inputs.get(f"comp{suffix}", companies[0])
            year = st.session_state.last_pred_inputs.get(f"year{suffix}", 2018)
            fuel = st.session_state.last_pred_inputs.get(f"fuel{suffix}", fuel_types[0])
            kms = st.session_state.last_pred_inputs.get(f"kms{suffix}", 50000)
            model_choice = st.session_state.last_pred_inputs.get(
                f"model{suffix}", next(iter(models.keys()))
            )
            compare_all = st.session_state.get(f"all{suffix}", False)

            car_age = CURRENT_YEAR - year
            fuel_simple = get_fuel_simple(fuel)
            input_df = pd.DataFrame(
                [
                    {
                        "car_age": car_age,
                        "kms_driven": kms,
                        "company": company,
                        "fuel_type_simple": fuel_simple,
                    }
                ]
            )

            header = (
                f"### {'🚗 Car A' if car_idx == 0 else '🚙 Car B'} Result"
                if ab_mode
                else "### 📊 Prediction Result"
            )
            st.markdown(header)

            with st.spinner("Computing prediction..."):
                pred = make_prediction(models[model_choice], input_df, preprocessor)
                tier, cls = get_price_tier(pred)

                # Data coverage
                similar_count = len(
                    df[
                        (df["company"] == company)
                        & (df["fuel_type"] == fuel)
                        & (df["car_age"].between(car_age - 2, car_age + 2))
                    ]
                )
                st.markdown(
                    f'<p style="color:#5a6270;font-size:0.8rem">Based on {similar_count:,} similar training examples</p>',
                    unsafe_allow_html=True,
                )

                # Main result card
                ci_pct = {"±10%": 0.1, "±15%": 0.15, "±20%": 0.2}.get(
                    st.session_state.get(f"ci{suffix}", "±15%"), 0.15
                )
                ci_val = pred * ci_pct
                st.markdown(
                    f'<div class="glass-card" style="text-align:center;padding:24px">'
                    f'<p style="color:#8892a0;font-size:0.9rem;margin:0">Estimated Price</p>'
                    f'<h1 class="shimmer" style="font-size:3rem;margin:4px 0">{fmt_inr(pred)}</h1>'
                    f'<p style="color:#c8ccd4;margin:0">Confidence Range: {fmt_inr(pred - ci_val)} – {fmt_inr(pred + ci_val)}'
                    f" ({st.session_state.get(f'ci{suffix}', '±15%')})</p>"
                    f'<p style="margin:8px 0"><span class="{cls}" style="font-size:0.9rem">{tier}</span>'
                    f" &nbsp;|&nbsp; Model: {model_choice} (R²={METRICS_DF[METRICS_DF['Model'] == model_choice]['Test R²'].values[0]:.4f})</p>"
                    f"</div>",
                    unsafe_allow_html=True,
                )

                # Depreciation curve
                years_future = list(range(6))
                dep_values = [pred * (0.85**y) for y in years_future]
                fig = go.Figure(
                    data=[
                        go.Scatter(
                            x=[f"Year {y}" if y > 0 else "Now" for y in years_future],
                            y=dep_values,
                            mode="lines+markers",
                            line={"color": "#e85d04", "width": 3},
                            marker={"size": 8, "color": "#e85d04"},
                            fill="tozeroy",
                            fillcolor="rgba(232,93,4,0.1)",
                        )
                    ]
                )
                fig.update_layout(title="Depreciation Curve (5-Year Forecast)", height=250)
                show_chart(fig, 250)

                # SMART PRICE EXPLAINER (Feature A)
                contribs = shap_lite_approximation(
                    models[model_choice],
                    input_df,
                    preprocessor,
                    pp_data["feature_names"],
                )
                explanation = generate_natural_language_explanation(contribs, pred * 0.5, pred)
                st.markdown(
                    f'<div class="glass-card" style="border-left:3px solid #4895ef">'
                    f'<strong style="color:#4895ef">🧠 Smart Price Explainer</strong><br>'
                    f'<span style="color:#c8ccd4">{explanation}</span></div>',
                    unsafe_allow_html=True,
                )

                # DEAL SCORE (Feature B) — speedometer gauge
                similar_actuals = df[(df["company"] == company) & (df["fuel_type"] == fuel)][
                    "Price"
                ]
                if len(similar_actuals) > 0:
                    avg_actual = similar_actuals.mean()
                    score = compute_deal_score(pred, avg_actual)
                    gauge_color = (
                        "#52b788" if score > 60 else ("#f48c06" if score > 40 else "#e85d04")
                    )
                    fig_gauge = go.Figure(
                        go.Indicator(
                            mode="gauge+number",
                            value=score,
                            title={
                                "text": "Deal Score",
                                "font": {"color": "#e8eaf0", "size": 14},
                            },
                            number={
                                "suffix": "/100",
                                "font": {"color": gauge_color, "size": 24},
                            },
                            gauge={
                                "axis": {
                                    "range": [0, 100],
                                    "tickcolor": "#8892a0",
                                    "tickwidth": 1,
                                },
                                "bar": {"color": gauge_color, "thickness": 0.3},
                                "bgcolor": "rgba(0,0,0,0)",
                                "borderwidth": 0,
                                "steps": [
                                    {"range": [0, 40], "color": "rgba(232,93,4,0.15)"},
                                    {
                                        "range": [40, 60],
                                        "color": "rgba(244,140,6,0.15)",
                                    },
                                    {
                                        "range": [60, 100],
                                        "color": "rgba(82,183,136,0.15)",
                                    },
                                ],
                                "threshold": {
                                    "line": {"color": gauge_color, "width": 4},
                                    "thickness": 0.75,
                                    "value": score,
                                },
                            },
                        )
                    )
                    fig_gauge.update_layout(
                        height=250,
                        paper_bgcolor="rgba(0,0,0,0)",
                        font={"color": "#e8eaf0", "family": "DM Sans"},
                    )
                    st.plotly_chart(fig_gauge, use_container_width=True)

                # ENSEMBLE PREDICTION (Feature C)
                ensemble_mean, spread, color = ensemble_prediction(models, input_df, preprocessor)
                if ensemble_mean:
                    st.markdown(
                        f'<div class="glass-card" style="border-left:3px solid {color}">'
                        f"<strong>🎯 Ensemble (Top-3 Avg): {fmt_inr(ensemble_mean)}</strong><br>"
                        f'<span style="color:#8892a0">Spread: {spread:.1f}% — '
                        f'<span style="color:{color}">{"Low" if color == "green" else "Medium" if color == "yellow" else "High"} variance</span></span>'
                        f"</div>",
                        unsafe_allow_html=True,
                    )

                # SHAP-lite waterfall (Feature D)
                if contribs:
                    names = [c[0][:20] for c in contribs[:5]]
                    vals = [c[1] for c in contribs[:5]]
                    base = pred - sum(vals)
                    waterfall_vals = [base] + vals
                    waterfall_names = ["Base"] + [f"{n}" for n in names]
                    ["#5a6270"] + ["#52b788" if v > 0 else "#e85d04" for v in vals]
                    fig2 = go.Figure(
                        data=[
                            go.Waterfall(
                                name="Contributions",
                                orientation="v",
                                measure=["absolute"] + ["relative"] * len(vals),
                                x=waterfall_names,
                                y=waterfall_vals,
                                text=[fmt_inr(v) for v in waterfall_vals],
                                connector={"line": {"color": "rgba(255,255,255,0.2)"}},
                                increasing={"marker_color": "#52b788"},
                                decreasing={"marker_color": "#e85d04"},
                                totals={"marker_color": "#4895ef"},
                            )
                        ]
                    )
                    fig2.update_layout(
                        title="Feature Contributions (SHAP-lite Waterfall)",
                        height=300,
                        showlegend=False,
                    )
                    show_chart(fig2, 300)

                # Compare all models
                if compare_all:
                    st.markdown("### All Model Predictions")
                    all_preds = []
                    for m_name, m_model in models.items():
                        p = make_prediction(m_model, input_df, preprocessor)
                        all_preds.append(
                            {
                                "Model": m_name,
                                "Prediction": p,
                                "R²": METRICS_DF[METRICS_DF["Model"] == m_name]["Test R²"].values[
                                    0
                                ],
                            }
                        )
                    preds_df = pd.DataFrame(all_preds)
                    fig3 = go.Figure(
                        data=[
                            go.Bar(
                                x=preds_df["Model"],
                                y=preds_df["Prediction"],
                                marker_color=[
                                    "#e85d04" if m == model_choice else "#4895ef"
                                    for m in preds_df["Model"]
                                ],
                                text=[fmt_inr(p) for p in preds_df["Prediction"]],
                                textposition="outside",
                            )
                        ]
                    )
                    fig3.update_layout(
                        title="All Models Comparison", xaxis_tickangle=-45, height=350
                    )
                    show_chart(fig3, 350)
                    st.dataframe(
                        preds_df.style.format({"Prediction": lambda x: fmt_inr(x), "R²": "{:.4f}"}),
                        use_container_width=True,
                    )

                # Similar cars
                if st.session_state.get(f"sim{suffix}", True):
                    st.markdown("### Similar Cars")
                    similar = df[
                        (df["company"] == company)
                        & (df["fuel_type"] == fuel)
                        & (df["car_age"].between(car_age - 3, car_age + 3))
                    ]
                    if len(similar) > 0:
                        similar = similar.copy()
                        similar["match_score"] = (
                            100
                            - np.abs(similar["car_age"] - car_age) * 10
                            - np.abs(similar["kms_driven"] - kms) / 5000
                        )
                        similar["match_score"] = similar["match_score"].clip(0, 100)
                        similar = similar.nlargest(5, "match_score")
                        for _, row in similar.iterrows():
                            st.markdown(
                                f'<div class="glass-card" style="padding:12px;display:flex;justify-content:space-between">'
                                f"<span><strong>{row['name']}</strong> · {row['year']} · {row['fuel_type']}</span>"
                                f'<span style="color:#e85d04">{fmt_inr(row["Price"])}</span>'
                                f'<span style="color:#52b788">{row["match_score"]:.0f}% match</span></div>',
                                unsafe_allow_html=True,
                            )
                    else:
                        st.info("No similar cars found for this exact configuration.")

                if ab_mode and car_idx == 0:
                    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)

        # AB Mode comparison
        if ab_mode and num_cars == 2:
            st.markdown("### 🏆 A/B Comparison Result")
            # Re-compute both predictions
            inputs = []
            for ci in range(2):
                s = f"_{ci}"
                comp = st.session_state.last_pred_inputs.get(f"comp{s}", companies[0])
                yr = st.session_state.last_pred_inputs.get(f"year{s}", 2018)
                fl = st.session_state.last_pred_inputs.get(f"fuel{s}", fuel_types[0])
                km = st.session_state.last_pred_inputs.get(f"kms{s}", 50000)
                mdl = st.session_state.last_pred_inputs.get(f"model{s}", next(iter(models.keys())))
                inp_df = pd.DataFrame(
                    [
                        {
                            "car_age": CURRENT_YEAR - yr,
                            "kms_driven": km,
                            "company": comp,
                            "fuel_type_simple": get_fuel_simple(fl),
                        }
                    ]
                )
                if mdl in models:
                    p = (
                        make_prediction(models[mdl], inp_df, preprocessor)
                        if preprocessor
                        else np.random.uniform(200000, 1500000)
                    )
                else:
                    p = np.random.uniform(200000, 1500000)
                inputs.append(
                    {
                        "label": "Car A" if ci == 0 else "Car B",
                        "comp": comp,
                        "year": yr,
                        "fuel": fl,
                        "kms": km,
                        "model": mdl,
                        "price": p,
                    }
                )
            if len(inputs) == 2:
                delta = inputs[0]["price"] - inputs[1]["price"]
                winner_idx = 0 if delta > 0 else 1
                loser_idx = 1 - winner_idx
                winner = inputs[winner_idx]
                loser = inputs[loser_idx]
                st.markdown(
                    f'<div class="glass-card" style="text-align:center;border:2px solid #52b788">'
                    f'<h2 style="color:#52b788;margin:0">🏆 {winner["label"]} Wins!</h2>'
                    f'<p style="color:#c8ccd4">{winner["label"]} ({fmt_inr(winner["price"])}) '
                    f'is <strong style="color:#e85d04">{fmt_inr(abs(delta))}</strong> '
                    f"{'more' if delta > 0 else 'less'} expensive than {loser['label']} ({fmt_inr(loser['price'])})</p>"
                    f"</div>",
                    unsafe_allow_html=True,
                )
                # Feature-level diff table
                diff_data = []
                for key in ["comp", "year", "fuel", "kms", "model"]:
                    diff_data.append(
                        {
                            "Attribute": key.capitalize(),
                            f"{inputs[0]['label']}": str(inputs[0][key]),
                            f"{inputs[1]['label']}": str(inputs[1][key]),
                        }
                    )
                diff_data.append(
                    {
                        "Attribute": "Price",
                        f"{inputs[0]['label']}": fmt_inr(inputs[0]["price"]),
                        f"{inputs[1]['label']}": fmt_inr(inputs[1]["price"]),
                    }
                )
                st.dataframe(pd.DataFrame(diff_data), use_container_width=True)


    # Bulk Prediction (Feature F)
    from app.pages.predictor_helpers import render_bulk_prediction, render_drift_simulator
    render_bulk_prediction(models, preprocessor)

    # Model Drift Simulator (Feature G)
    render_drift_simulator(df)
