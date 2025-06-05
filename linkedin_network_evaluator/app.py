"""Streamlit application for Intero Insight Network Analysis (Lite)."""

import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt

from .data_loader import load_connections
from .analysis import (
    company_frequency,
    position_frequency,
    add_seniority_column,
    seniority_distribution,
    kpi_metrics,
    connections_heatmap,
    seniority_by_company_pivot,
    connection_anniversary,
    latest_connections,
)


def main() -> None:
    """Run the Streamlit web application."""
    st.set_page_config(page_title="Intero Insight Network Analysis (Lite)", layout="wide")
    st.title("Intero Insight Network Analysis (Lite)")

    uploaded_file = st.file_uploader("Upload your LinkedIn Connections.csv", type="csv")

    if uploaded_file is not None:
        try:
            df = load_connections(uploaded_file)
        except Exception as exc:
            st.error(f"Failed to load file: {exc}")
        else:
            df = add_seniority_column(df)
            metrics = kpi_metrics(df)
            col1, col2, col3, col4, col5 = st.columns(5)
            col1.metric("Total Connections", int(metrics["total"]))
            col2.metric("Added Last 30 Days", int(metrics["added_30"]))
            col3.metric("Added This Year", int(metrics["added_year"]))
            col4.metric("Median Connections/Month", f"{metrics['median_per_month']:.1f}")
            col5.metric("Longest Streak", f"{metrics['longest_streak']} days")

            left, right = st.columns(2)

            with left:
                st.subheader("Connections by Year-Month")
                heatmap = connections_heatmap(df)
                if not heatmap.empty:
                    st.plotly_chart(px.imshow(heatmap, text_auto=True), use_container_width=True)

                st.subheader("Seniority Distribution by Company")
                pivot = seniority_by_company_pivot(df)
                if not pivot.empty:
                    fig, ax = plt.subplots(figsize=(10, 12))
                    cumulative = None
                    for tier in pivot.columns:
                        if cumulative is None:
                            ax.barh(pivot.index, pivot[tier], label=tier)
                            cumulative = pivot[tier].copy()
                        else:
                            ax.barh(pivot.index, pivot[tier], left=cumulative, label=tier)
                            cumulative += pivot[tier]
                    ax.set_xlabel("Connections")
                    ax.set_title("Seniority distribution across your 25 most-connected companies")
                    ax.legend(title="Seniority", bbox_to_anchor=(1.02, 1), loc="upper left")
                    st.pyplot(fig)

                st.subheader("Connection Anniversary")
                anniv = connection_anniversary(df)
                if not anniv.empty:
                    st.dataframe(anniv)

                st.subheader("Latest 25 Connections")
                st.dataframe(latest_connections(df))


            with right:
                st.subheader("Top Companies")
                comp_freq = company_frequency(df)
                st.dataframe(comp_freq.head(20).reset_index().rename(columns={"index": "Company", "Company": "Count"}))

                st.subheader("Position Title Frequency")
                pos_freq = position_frequency(df)
                st.dataframe(pos_freq.reset_index().rename(columns={"index": "Position", "Position": "Count"}))

                st.subheader("Seniority Distribution")
                seniority_dist = seniority_distribution(df)
                st.plotly_chart(px.bar(seniority_dist), use_container_width=True)

            st.download_button(
                "Email me a deeper dive?",
                data="PDF export is not implemented in this demo.",
                file_name="report.txt",
            )
    else:
        st.info("Please upload your Connections.csv file to begin analysis.")


if __name__ == "__main__":
    main()
