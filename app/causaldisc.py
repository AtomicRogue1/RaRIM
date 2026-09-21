from database import connect_to_db

import pandas as pd
import numpy as np

from tigramite import data_processing as pp
from tigramite.lpcmci import LPCMCI
from tigramite.independence_tests.parcorr import ParCorr


def LPCMCI_causal_analysis(COMPANY):
    TAU_MAX = 10
    PC_ALPHA = 0.05
    MISSING_VALUE = 999.0


    # ==================================================
    # DATABASE
    # ==================================================

    conn = connect_to_db()

    try:
        with conn.cursor() as cursor:

            cursor.execute("""
                SELECT
                    collected_at,
                    sentiment_score,
                    risk_category
                FROM articles
                WHERE company = %s
                AND sentiment_score IS NOT NULL
                AND risk_category IS NOT NULL
                ORDER BY collected_at
            """, (COMPANY,))

            rows = cursor.fetchall()

    finally:
        conn.close()


    # ==================================================
    # CREATE DATAFRAME
    # ==================================================

    df = pd.DataFrame(
        rows,
        columns=[
            "collected_at",
            "sentiment_score",
            "risk_category"
        ]
    )

    df["collected_at"] = pd.to_datetime(df["collected_at"])

    print(f"\nArticles retrieved for {COMPANY}: {len(df)}")

    print("\nRisk categories found:")
    print(df["risk_category"].value_counts())


    # ==================================================
    # DAILY SENTIMENT
    # ==================================================

    # Calculate mean sentiment for all articles on each day

    daily_sentiment = (
        df
        .groupby("collected_at")
        .agg(
            sentiment_score=("sentiment_score", "mean")
        )
    )


    # ==================================================
    # CONVERT RISK CATEGORIES TO NUMERICAL COUNTS
    # ==================================================

    # Count how many articles of each risk category
    # occur on each day.

    risk_counts = (
        df
        .groupby(["collected_at", "risk_category"])
        .size()
        .unstack(fill_value=0)
    )


    # ==================================================
    # RENAME RISK CATEGORIES
    # ==================================================

    risk_counts = risk_counts.rename(
        columns={
            "Financial Risks": "financial_risk",
            "Product Risks": "product_risk",
            "Legal Risks": "legal_risk",
            "Reputational Risks": "reputational_risk",
            "Governance Risks": "governance_risk",
            "Political Unrest": "political_unrest"
        }
    )


    risk_columns = [
        "financial_risk",
        "product_risk",
        "legal_risk",
        "reputational_risk",
        "governance_risk",
        "political_unrest"
    ]


    # ==================================================
    # MAKE SURE ALL RISK COLUMNS EXIST
    # ==================================================

    # For example, if Tesla has no Political Unrest
    # articles at all, pandas wouldn't automatically
    # create that column.

    for column in risk_columns:

        if column not in risk_counts.columns:
            risk_counts[column] = 0


    # Keep only the six risk variables
    risk_counts = risk_counts[risk_columns]


    # ==================================================
    # COMBINE SENTIMENT + RISK DATA
    # ==================================================

    daily_df = daily_sentiment.join(risk_counts)

    daily_df = daily_df.sort_index()


    # ==================================================
    # CREATE CONTINUOUS DAILY TIME SERIES
    # ==================================================

    # Create every calendar day between the first
    # and last observation.
    #
    # This means:
    #
    # tau = 1  -> 1 day
    # tau = 2  -> 2 days
    # ...
    # tau = 10 -> 10 days

    daily_df = daily_df.asfreq("D")


    # ==================================================
    # HANDLE DAYS WITH NO NEWS
    # ==================================================

    # If there are no articles on a particular day,
    # there are zero articles belonging to each risk
    # category.

    daily_df[risk_columns] = (
        daily_df[risk_columns]
        .fillna(0)
    )


    # IMPORTANT:
    #
    # sentiment_score is NOT filled with 0.
    #
    # No news does not necessarily mean neutral sentiment.
    # Therefore sentiment remains NaN and Tigramite will
    # treat it as missing data.


    # ==================================================
    # INSPECT FINAL DATAFRAME
    # ==================================================

    print("\n========================================")
    print("FINAL DAILY DATAFRAME")
    print("========================================")

    print(daily_df)


    print("\n========================================")
    print("MISSING VALUES")
    print("========================================")

    print(daily_df.isna().sum())


    print("\n========================================")
    print("TOTAL RISK COUNTS")
    print("========================================")

    print(daily_df[risk_columns].sum())


    # ==================================================
    # TIGRAMITE VARIABLES
    # ==================================================

    variables = [
        "sentiment_score",
        "financial_risk",
        "product_risk",
        "legal_risk",
        "reputational_risk",
        "governance_risk",
        "political_unrest"
    ]


    print("\n========================================")
    print("VARIABLE NUMBERS")
    print("========================================")

    for index, variable in enumerate(variables):
        print(f"{index} = {variable}")


    # ==================================================
    # CONVERT DATAFRAME TO NUMPY
    # ==================================================

    data = daily_df[variables].to_numpy(dtype=float)


    # ==================================================
    # HANDLE MISSING SENTIMENT
    # ==================================================

    # Tigramite does not accept ordinary NaN values.
    #
    # Replace NaN with a special value and tell
    # Tigramite that this value means "missing".

    data = np.where(
        np.isnan(data),
        MISSING_VALUE,
        data
    )


    # ==================================================
    # CREATE TIGRAMITE DATAFRAME
    # ==================================================

    tigramite_df = pp.DataFrame(
        data=data,
        var_names=variables,
        datatime=daily_df.index.to_numpy(),
        missing_flag=MISSING_VALUE
    )


    # ==================================================
    # CONDITIONAL INDEPENDENCE TEST
    # ==================================================

    cond_ind_test = ParCorr(
        significance="analytic"
    )


    # ==================================================
    # CREATE LPCMCI
    # ==================================================

    lpcmci = LPCMCI(
        dataframe=tigramite_df,
        cond_ind_test=cond_ind_test,
        verbosity=1
    )


    # ==================================================
    # RUN LPCMCI
    # ==================================================

    results = lpcmci.run_lpcmci(
        tau_max=TAU_MAX,
        pc_alpha=PC_ALPHA
    )


    # ==================================================
    # RESULTS
    # ==================================================

    graph = results["graph"]
    p_matrix = results["p_matrix"]
    val_matrix = results["val_matrix"]


    print("\n========================================")
    print("RAW GRAPH")
    print("========================================")

    print(graph)


    # ==================================================
    # HUMAN-READABLE RELATIONSHIPS
    # ==================================================

    res = []

    print("\n========================================")
    print("DISCOVERED RELATIONSHIPS")
    print("========================================")

    relationship_found = False


    for source_index, source_variable in enumerate(variables):

        for target_index, target_variable in enumerate(variables):

            for tau in range(TAU_MAX + 1):

                resres = {}

                edge = graph[
                    source_index,
                    target_index,
                    tau
                ]

                # Empty string means no edge
                if edge == "":
                    continue

                relationship_found = True

                p_value = p_matrix[
                    source_index,
                    target_index,
                    tau
                ]

                test_statistic = val_matrix[
                    source_index,
                    target_index,
                    tau
                ]

                print("\n----------------------------------------")

                # Same-day relationship
                if tau == 0:

                    print(
                        f"{source_variable}(today) "
                        f"{edge} "
                        f"{target_variable}(today)"
                    )

                    print("Lag: same day")

                    resres["Lag"] = 0

                # Lagged relationship
                else:

                    print(
                        f"{source_variable}(t-{tau}) "
                        f"{edge} "
                        f"{target_variable}(today)"
                    )

                    print(
                        f"Lag: {tau} day(s)"
                    )
                    resres["Lag"] = tau

                print(
                    f"P-value: {p_value:.6f}"
                )

                print(
                    f"Test statistic: {test_statistic:.4f}"
                )

                resres = {
                    "Source": source_variable,
                    "Target": target_variable,
                    "Edge": edge,
                    "Lag": tau,
                    "P-value": round(float(p_value), 6),
                    "Test statistic": round(float(test_statistic), 4)
                    }

                res.append(resres)

    if not relationship_found:
        print(
            "\nNo relationships were retained "
            "by LPCMCI with the current settings."
        )
        return -1
    else:
        return res