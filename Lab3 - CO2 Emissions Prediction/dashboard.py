import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.metrics import mean_absolute_error

st.set_page_config(page_title="CO2 Prediction - Polynomial Regression", layout="wide")

st.title("CO2 Emissions Prediction - China Steel Industry")
st.markdown("Polynomial regression (degree 1-3) with dynamic confidence interval using residuals")

# --- Upload CSV ---
uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    df = df.dropna(subset=["Owner", "Year", "Total_CO2_Emissions"])
    df["Year"] = df["Year"].astype(int)
    df["Total_CO2_Emissions"] = df["Total_CO2_Emissions"].astype(float)

    # --- Company selection ---
    companies = sorted(df["Owner"].unique())
    selected_company = st.selectbox("Select a company", companies)
    company_data = df[df["Owner"] == selected_company].sort_values("Year")

    # --- Degree selection (1, 2, 3) ---
    degree = st.radio("Select polynomial degree", options=[1, 2, 3], index=1)

    X = company_data["Year"].values.reshape(-1,1)
    y = company_data["Total_CO2_Emissions"].values
    n = len(y)

    poly = PolynomialFeatures(degree=degree)
    X_poly = poly.fit_transform(X)

    model = LinearRegression()
    model.fit(X_poly, y)
    y_pred = model.predict(X_poly)

    # --- Residuals ---
    residuals = y - y_pred
    mae = mean_absolute_error(y, y_pred)
    s = np.std(residuals)  # Use residual std as dynamic CI

    # --- Future predictions ---
    last_year = company_data["Year"].max()
    future_years = np.arange(last_year + 1, 2031)
    all_years = np.concatenate([company_data["Year"], future_years])
    all_X_poly = poly.transform(all_years.reshape(-1,1))
    all_pred = model.predict(all_X_poly)

    # --- Dynamic CI using residuals ---
    # Wider intervals for years farther from historical data
    distance_factor = np.sqrt(1 + ((all_years - np.mean(X))**2) / np.sum((X.flatten() - np.mean(X))**2))
    upper = all_pred + 2 * s * distance_factor  # ~95% CI
    lower = all_pred - 2 * s * distance_factor

    # --- Plot ---
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=company_data["Year"], y=y,
        mode="markers+lines",
        name="Actual Emissions",
        line=dict(color="#3b82f6")
    ))
    fig.add_trace(go.Scatter(
        x=all_years, y=all_pred,
        mode="lines+markers",
        name=f"Polynomial Regression (degree={degree})",
        line=dict(color="#ef4444", dash="dash")
    ))
    fig.add_trace(go.Scatter(
        x=np.concatenate([all_years, all_years[::-1]]),
        y=np.concatenate([upper, lower[::-1]]),
        fill='toself',
        fillcolor='rgba(239,68,68,0.2)',
        line=dict(color='rgba(255,255,255,0)'),
        hoverinfo="skip",
        name="95% Confidence Interval"
    ))
    fig.update_layout(
        title=f"CO2 Emissions Forecast - {selected_company}",
        xaxis_title="Year",
        yaxis_title="CO2 Emissions (tonnes)",
        template="plotly_white"
    )
    st.plotly_chart(fig, use_container_width=True)

    # --- Metrics ---
    r2 = model.score(X_poly, y)
    trend = "↑" if all_pred[-1] - all_pred[0] > 0 else "↓"
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("R²", f"{r2:.3f}")
    col2.metric("RMSE", f"{np.sqrt(np.mean(residuals**2)):.0f}")
    col3.metric("MAE", f"{mae:.0f}")
    col4.metric("Trend", trend)