import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import numpy as np

st.set_page_config(page_title="Phi-Filter Dashboard", page_icon="📈", layout="wide")

st.title("Phi-Harmonic Trading Signal Filter Dashboard")
st.markdown("Real-time signal visualization and harmonic lattice exploration")

# Configuration
API_BASE = st.sidebar.text_input("API Base URL", "http://localhost:8000")
API_KEY = st.sidebar.text_input("API Key", "phi-filter-dev-key-2026", type="password")

# Tabs
tab1, tab2, tab3 = st.tabs(["Signal Filtering", "Harmonic Lattice", "Batch Analysis"])

with tab1:
    st.header("Single Signal Filtering")

    col1, col2 = st.columns(2)

    with col1:
        price = st.number_input("Price", value=100.0, min_value=0.01)
        volatility = st.slider("Volatility (%)", 0.1, 50.0, 10.0)

    with col2:
        direction = st.selectbox("Direction", ["long", "short"])
        market = st.selectbox("Market", ["equity", "forex", "crypto", "futures"])

    if st.button("Filter Signal"):
        payload = {
            "price": price,
            "volatility": volatility / 100.0,
            "direction": direction,
            "market": market,
        }

        headers = {"X-API-KEY": API_KEY}

        try:
            response = requests.post(
                f"{API_BASE}/filter", json=payload, headers=headers
            )

            if response.status_code == 200:
                result = response.json()
                st.success("Signal processed successfully!")

                # Display result
                if result["feasible"]:
                    st.info("✅ Signal is geometrically feasible")
                else:
                    st.warning("❌ Signal rejected as geometrically infeasible")

                # Show details
                with st.expander("Filter Details"):
                    st.json(result)

            else:
                st.error(f"API Error: {response.status_code} - {response.text}")

        except Exception as e:
            st.error(f"Connection Error: {str(e)}")

with tab2:
    st.header("Harmonic Lattice Exploration")

    base_price = st.number_input("Base Price", value=100.0, min_value=0.01)
    volatility = st.slider(
        "Volatility for Filtering (%)", 0.1, 50.0, 10.0, key="harmonic_vol"
    )

    if st.button("Generate Harmonic Lattice"):
        payload = {"base_price": base_price, "volatility": volatility / 100.0}

        headers = {"X-API-KEY": API_KEY}

        try:
            response = requests.post(
                f"{API_BASE}/filter/harmonic", json=payload, headers=headers
            )

            if response.status_code == 200:
                result = response.json()

                # Extract levels
                levels = result["harmonic_levels"]
                feasible_levels = [level for level in levels if level["feasible"]]
                rejected_levels = [level for level in levels if not level["feasible"]]

                # Create visualization
                fig = go.Figure()

                # Add base price
                fig.add_trace(
                    go.Scatter(
                        x=[0],
                        y=[base_price],
                        mode="markers",
                        name="Base Price",
                        marker=dict(size=12, color="red"),
                    )
                )

                # Add feasible levels
                if feasible_levels:
                    y_feasible = [level["level"] for level in feasible_levels]
                    fig.add_trace(
                        go.Scatter(
                            x=[1] * len(y_feasible),
                            y=y_feasible,
                            mode="markers",
                            name="Feasible Levels",
                            marker=dict(size=8, color="green"),
                        )
                    )

                # Add rejected levels
                if rejected_levels:
                    y_rejected = [level["level"] for level in rejected_levels]
                    fig.add_trace(
                        go.Scatter(
                            x=[1] * len(y_rejected),
                            y=y_rejected,
                            mode="markers",
                            name="Rejected Levels",
                            marker=dict(size=6, color="red", symbol="x"),
                        )
                    )

                fig.update_layout(
                    title="Harmonic Lattice Levels",
                    xaxis_title="Level Type",
                    yaxis_title="Price Level",
                    xaxis=dict(tickvals=[0, 1], ticktext=["Base", "Lattice"]),
                    showlegend=True,
                )

                st.plotly_chart(fig, use_container_width=True)

                # Show statistics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Levels", len(levels))
                with col2:
                    st.metric("Feasible Levels", len(feasible_levels))
                with col3:
                    st.metric("Rejection Rate", ".1f")

                # Show level details
                with st.expander("Level Details"):
                    df = pd.DataFrame(levels)
                    st.dataframe(df)

            else:
                st.error(f"API Error: {response.status_code} - {response.text}")

        except Exception as e:
            st.error(f"Connection Error: {str(e)}")

with tab3:
    st.header("Batch Signal Analysis")

    uploaded_file = st.file_uploader("Upload CSV with signals", type="csv")

    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.write("Preview of uploaded data:")
        st.dataframe(df.head())

        if st.button("Analyze Batch"):
            # Convert to list of dicts
            signals = df.to_dict("records")

            payload = {"signals": signals}
            headers = {"X-API-KEY": API_KEY}

            try:
                response = requests.post(
                    f"{API_BASE}/filter/batch", json=payload, headers=headers
                )

                if response.status_code == 200:
                    results = response.json()

                    # Create summary
                    feasible_count = sum(1 for r in results if r["feasible"])
                    total_count = len(results)

                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Signals", total_count)
                    with col2:
                        st.metric("Feasible Signals", feasible_count)
                    with col3:
                        st.metric("Win Rate", ".1f")

                    # Visualization
                    labels = ["Feasible", "Rejected"]
                    values = [feasible_count, total_count - feasible_count]

                    fig = go.Figure(data=[go.Pie(labels=labels, values=values)])
                    fig.update_layout(title="Signal Feasibility Distribution")
                    st.plotly_chart(fig, use_container_width=True)

                    # Results table
                    results_df = pd.DataFrame(results)
                    st.dataframe(results_df)

                else:
                    st.error(f"API Error: {response.status_code} - {response.text}")

            except Exception as e:
                st.error(f"Connection Error: {str(e)}")

# Usage stats
st.sidebar.markdown("---")
st.sidebar.header("Usage Stats")

if st.sidebar.button("Get Usage Stats"):
    headers = {"X-API-KEY": API_KEY}

    try:
        response = requests.get(f"{API_BASE}/usage", headers=headers)

        if response.status_code == 200:
            usage = response.json()
            st.sidebar.metric("Requests Today", usage.get("requests_today", 0))
            st.sidebar.metric("Rate Limit Remaining", usage.get("remaining", 0))
        else:
            st.sidebar.error("Failed to fetch usage")

    except Exception as e:
        st.sidebar.error("Connection error")
