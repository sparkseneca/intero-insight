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

    st.markdown(
        """
        <style>
            html, body, [data-testid="stApp"] {
                font-family: 'Open Sans', sans-serif;
                background-color: #f3f4f6;
                color: #084c6d;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.title("Intero Insight Network Analysis (Lite)")

    uploaded_file = st.file_uploader("Upload your LinkedIn Connections.csv", type="csv")

    with st.expander("How do I export this file from LinkedIn?"):
        st.markdown(
            """
1. **Log into LinkedIn** and open your [data export settings](https://www.linkedin.com/psettings/member-data).
2. Choose **Connections** and click **Request archive**.
3. Wait for the email from LinkedIn and download the ZIP file.
4. Unzip it and open `Connections.csv`.
            """
        )

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
                st.subheader("Connections by Month")
                st.caption("Analyze the density and timing of your new connections.")
                heatmap = connections_heatmap(df)
                if not heatmap.empty:
                    st.plotly_chart(px.imshow(heatmap, text_auto=True), use_container_width=True)
                st.divider()

                st.subheader("Seniority Distribution by Company")
                st.caption("See how you are connected across levels at top organizations.")
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
                st.divider()

                st.subheader("Connection Anniversary")
                st.caption("People you connected with on this day in past years.")
                anniv = connection_anniversary(df)
                if not anniv.empty:
                    st.dataframe(anniv)
                st.divider()

                st.subheader("Recent Connections")
                st.caption("Review the latest additions to your network.")
                st.dataframe(latest_connections(df))


            with right:
                st.subheader("Top Companies by Connection")
                st.caption("Who engages with you the most on LinkedIn.")
                comp_freq = company_frequency(df)
                st.dataframe(comp_freq.head(20).reset_index().rename(columns={"index": "Company", "Company": "Count"}))
                st.divider()

                st.subheader("Position Title Frequency")
                st.caption("Common titles found across your network.")
                pos_freq = position_frequency(df)
                st.dataframe(pos_freq.reset_index().rename(columns={"index": "Position", "Position": "Count"}))
                st.divider()

                st.subheader("Seniority Distribution")
                st.caption("Overall seniority mix of your connections.")
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
