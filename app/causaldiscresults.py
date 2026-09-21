from causaldisc import LPCMCI_causal_analysis

import streamlit as st
import pandas as pd


def causal_disc_results(COMPANY):

    # ------------------------------------------
    # Run causal discovery
    # ------------------------------------------

    with st.spinner(
        f"Running causal discovery for {COMPANY}..."
    ):
        discovery = LPCMCI_causal_analysis(COMPANY)


    # ------------------------------------------
    # Check results
    # ------------------------------------------

    if not discovery:
        st.warning(
            "No causal relationships were discovered."
        )
        return


    # Convert to DataFrame
    df = pd.DataFrame(discovery)


    # ------------------------------------------
    # Clean numeric columns
    # ------------------------------------------

    df["P-value"] = pd.to_numeric(
        df["P-value"],
        errors="coerce"
    )

    df["Test statistic"] = pd.to_numeric(
        df["Test statistic"],
        errors="coerce"
    )


    # ------------------------------------------
    # FILTER STRONG CAUSAL CANDIDATES
    # ------------------------------------------

    strong = df[
        (df["Edge"] == "-->") &
        (df["Lag"] > 0) &
        (df["P-value"] < 0.01) &
        (df["Test statistic"].abs() >= 0.30)
    ].copy()


    # Sort strongest first
    strong = strong.sort_values(
        by="Test statistic",
        key=lambda x: x.abs(),
        ascending=False
    )


    # ------------------------------------------
    # STREAMLIT OUTPUT
    # ------------------------------------------

    st.subheader(f"Causal Discovery — {COMPANY}")

    if strong.empty:

        st.info(
            "No strong directed lagged causal candidates "
            "were identified with the current thresholds."
        )

        return


    st.success(
        f"{len(strong)} strong causal candidate(s) identified."
    )


    # ------------------------------------------
    # DISPLAY EACH DISCOVERY
    # ------------------------------------------
    col_left, col_right = st.columns(2)

    for i, (_, result) in enumerate(strong.iterrows()):

        source = result["Source"].replace("_", " ").title()
        target = result["Target"].replace("_", " ").title()

        lag = int(result["Lag"])
        p_value = result["P-value"]
        statistic = result["Test statistic"]

        # Alternate between left and right columns
        column = col_left if i % 2 == 0 else col_right

        with column:

            with st.container(border=True):

                st.markdown(
                    f"### {source} → {target}"
                )

                st.markdown(
                    f"**Time lag:** {lag} day{'s' if lag != 1 else ''}"
                )

                metric_col1, metric_col2 = st.columns(2)

                with metric_col1:
                    st.metric(
                        "P-value",
                        f"{p_value:.6f}"
                    )

                with metric_col2:
                    st.metric(
                        "Test statistic",
                        f"{statistic:.3f}"
                    )

                # Interpretation
                if statistic > 0:

                    st.write(
                        f"Higher **{source.lower()}** activity is "
                        f"conditionally associated with higher "
                        f"**{target.lower()}** activity approximately "
                        f"{lag} day{'s' if lag != 1 else ''} later."
                    )

                else:

                    st.write(
                        f"Higher **{source.lower()}** activity is "
                        f"conditionally associated with lower "
                        f"**{target.lower()}** activity approximately "
                        f"{lag} day{'s' if lag != 1 else ''} later."
                    )

                st.caption(
                    "This is a causal candidate identified by LPCMCI, "
                    "not proof of a causal effect."
                )

    with st.expander("View all LPCMCI relationships"):

        st.dataframe(
            df,
            width="stretch",
            hide_index=True
        )