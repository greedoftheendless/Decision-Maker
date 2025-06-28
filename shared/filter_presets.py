def apply_preset_filtration(df, preset_name):
    """
    Applies comprehensive filtration based on preset selection.
    Returns filtered dataframe and filter summary.
    """
    if df is None or df.empty:
        return df, {}
    
    filtered_df = df.copy()
    applied_filters = {}
    
    if preset_name == "Gaming":
        if "Weight (g)" in df.columns:
            condition = (df["Weight (g)"] <= 90) & (df["Weight (g)"].notna())
            filtered_df = filtered_df[condition]
            applied_filters["Weight"] = "≤ 90g (lightweight for fast movements)"
        
        if "Shape" in df.columns:
            condition = df["Shape"].astype(str).str.contains("Symmetrical", case=False, na=False)
            filtered_df = filtered_df[condition]
            applied_filters["Shape"] = "Symmetrical (ambidextrous gaming)"
        
        if "Side buttons" in df.columns:
            condition = (df["Side buttons"] >= 2) & (df["Side buttons"].notna())
            filtered_df = filtered_df[condition]
            applied_filters["Side buttons"] = "≥ 2 (essential gaming functions)"
        
        if "Hand compatibility" in df.columns:
            condition = df["Hand compatibility"].isin(["Right", "Both"])
            filtered_df = filtered_df[condition]
            applied_filters["Hand compatibility"] = "Right or Both"
        
        if "DPI" in df.columns:
            condition = (df["DPI"] >= 3000) & (df["DPI"].notna())
            filtered_df = filtered_df[condition]
            applied_filters["DPI"] = "≥ 3000 (high precision)"
        
        if "Polling rate" in df.columns:
            condition = (df["Polling rate"] >= 500) & (df["Polling rate"].notna())
            filtered_df = filtered_df[condition]
            applied_filters["Polling rate"] = "≥ 500Hz (responsive)"
    
    elif preset_name == "Normal":
        if "Weight (g)" in df.columns:
            condition = (df["Weight (g)"] >= 70) & (df["Weight (g)"] <= 120) & (df["Weight (g)"].notna())
            filtered_df = filtered_df[condition]
            applied_filters["Weight"] = "70-120g (comfortable for daily use)"
        
        if "Side buttons" in df.columns:
            condition = (df["Side buttons"] <= 3) & (df["Side buttons"].notna())
            filtered_df = filtered_df[condition]
            applied_filters["Side buttons"] = "≤ 3 (not overwhelming)"
        
        if "Connectivity" in df.columns:
            condition = df["Connectivity"].astype(str).str.contains("Wireless|USB", case=False, na=False)
            filtered_df = filtered_df[condition]
            applied_filters["Connectivity"] = "Wireless or USB (reliable)"
    
    elif preset_name == "Editing":
        if "Side buttons" in df.columns:
            condition = (df["Side buttons"] >= 3) & (df["Side buttons"].notna())
            filtered_df = filtered_df[condition]
            applied_filters["Side buttons"] = "≥ 3 (macro functions)"
        
        if "Weight (g)" in df.columns:
            condition = (df["Weight (g)"] >= 80) & (df["Weight (g)"].notna())
            filtered_df = filtered_df[condition]
            applied_filters["Weight"] = "≥ 80g (stability for precision)"
        
        if "DPI" in df.columns:
            condition = (df["DPI"] >= 1000) & (df["DPI"].notna())
            filtered_df = filtered_df[condition]
            applied_filters["DPI"] = "≥ 1000 (precision work)"
        
        if "Middle buttons" in df.columns:
            condition = (df["Middle buttons"] >= 1) & (df["Middle buttons"].notna())
            filtered_df = filtered_df[condition]
            applied_filters["Middle buttons"] = "≥ 1 (scroll wheel functions)"
    
    elif preset_name == "Ergonomic":
        if "Shape" in df.columns:
            condition = df["Shape"].astype(str).str.contains("Ergonomic", case=False, na=False)
            filtered_df = filtered_df[condition]
            applied_filters["Shape"] = "Ergonomic (comfortable grip)"
        
        if "Thumb rest" in df.columns:
            condition = df["Thumb rest"].astype(str).str.contains("Yes", case=False, na=False)
            filtered_df = filtered_df[condition]
            applied_filters["Thumb rest"] = "Yes (reduces strain)"
        
        if "Hand compatibility" in df.columns:
            condition = df["Hand compatibility"].isin(["Right", "Left", "Both"])
            filtered_df = filtered_df[condition]
            applied_filters["Hand compatibility"] = "Specific hand support"
        
        if "Material" in df.columns:
            condition = df["Material"].astype(str).str.contains("Rubber|Soft|Textured", case=False, na=False)
            filtered_df = filtered_df[condition]
            applied_filters["Material"] = "Comfortable grip materials"
    
    elif preset_name == "Compact":
        if "Weight (g)" in df.columns:
            condition = (df["Weight (g)"] <= 80) & (df["Weight (g)"].notna())
            filtered_df = filtered_df[condition]
            applied_filters["Weight"] = "≤ 80g (portable)"
        
        if "Size" in df.columns:
            condition = df["Size"].astype(str).str.contains("Small|Compact", case=False, na=False)
            filtered_df = filtered_df[condition]
            applied_filters["Size"] = "Small/Compact (travel-friendly)"
        
        if "Connectivity" in df.columns:
            condition = df["Connectivity"].astype(str).str.contains("Wireless", case=False, na=False)
            filtered_df = filtered_df[condition]
            applied_filters["Connectivity"] = "Wireless (no cables)"
        
        if "Side buttons" in df.columns:
            condition = (df["Side buttons"] <= 2) & (df["Side buttons"].notna())
            filtered_df = filtered_df[condition]
            applied_filters["Side buttons"] = "≤ 2 (minimal design)"
    
    return filtered_df, applied_filters
