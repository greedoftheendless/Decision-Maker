# shared/custom_filters.py

def apply_weight_category_filter(df, weight_category):
    """
    Filters df by weight categories:
    Light: <80g
    Medium: 80-99g
    Heavy: >=100g
    """
    if df is None or df.empty or weight_category == "" or "Weight (g)" not in df.columns:
        return df

    filtered = df.copy()
    if weight_category == "Light":
        filtered = filtered[filtered["Weight (g)"] < 80]
    elif weight_category == "Medium":
        filtered = filtered[(filtered["Weight (g)"] >= 80) & (filtered["Weight (g)"] <= 99)]
    elif weight_category == "Heavy":
        filtered = filtered[filtered["Weight (g)"] >= 100]

    return filtered


def apply_length_category_filter(df, length_category):
    """
    Filters df by volume categories (instead of length):
    Small: volume < 287907 mm^3
    Medium: 287907 <= volume <= 324720
    Large: volume > 324720
    Assumes df has a 'Volume' column with numeric volume values.
    """
    if df is None or df.empty or length_category == "" or "Volume" not in df.columns:
        return df

    filtered = df.copy()
    if length_category == "Small":
        filtered = filtered[filtered["Volume"] < 287907]
    elif length_category == "Medium":
        filtered = filtered[(filtered["Volume"] >= 287907) & (filtered["Volume"] <= 324720)]
    elif length_category == "Large":
        filtered = filtered[filtered["Volume"] > 324720]

    return filtered


def apply_custom_filters(df, filters):
    if df is None or df.empty:
        return df

    filtered = df.copy()

    if "dpi_range" in filters and "DPI" in filtered.columns:
        dpi_min, dpi_max = filters["dpi_range"]
        filtered = filtered[
            (filtered["DPI"] >= dpi_min) & (filtered["DPI"] <= dpi_max)
        ]

    if "polling_rate_range" in filters and "Polling rate" in filtered.columns:
        poll_min, poll_max = filters["polling_rate_range"]
        filtered = filtered[
            (filtered["Polling rate"] >= poll_min) & (filtered["Polling rate"] <= poll_max)
        ]

    # Apply weight category filter
    if "weight_category" in filters:
        filtered = apply_weight_category_filter(filtered, filters["weight_category"])

    # Apply length category filter (using volume)
    if "length_category" in filters:
        filtered = apply_length_category_filter(filtered, filters["length_category"])

    return filtered


def apply_categorical_filters(df, category_filters):
    if df is None or df.empty:
        return df

    filtered = df.copy()

    for col, selected_values in category_filters.items():
        if col in filtered.columns and selected_values:
            filtered = filtered[
                filtered[col].astype(str).isin(selected_values)
            ]

    return filtered


def apply_checkbox_filters(df, check_filters):
    if df is None or df.empty:
        return df

    filtered = df.copy()

    for col, accepted_values in check_filters.items():
        if col in filtered.columns and accepted_values:
            filtered = filtered[
                filtered[col].astype(str).str.lower().isin(
                    [v.lower() for v in accepted_values]
                )
            ]

    return filtered
