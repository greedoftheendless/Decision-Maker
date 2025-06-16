import streamlit as st
import pandas as pd
from shared.data_reader import read_dataset

st.set_page_config(page_title="🖱️ Mouse Decision Maker", layout="wide")
st.title("🖱️ Mouse Decision Maker")

# Session state initialization
if "show_filters" not in st.session_state:
    st.session_state.show_filters = True
if "filters_applied" not in st.session_state:
    st.session_state.filters_applied = False
if "type_option" not in st.session_state:
    st.session_state.type_option = ""
if "wired_checked" not in st.session_state:
    st.session_state.wired_checked = False
if "wireless_checked" not in st.session_state:
    st.session_state.wireless_checked = False
if "selected_brands" not in st.session_state:
    st.session_state.selected_brands = []
if "selected_mouse_names" not in st.session_state:
    st.session_state.selected_mouse_names = []

# Helper function to find relevant column by keywords
def find_column(df_columns, keywords):
    lowered = [c.lower() for c in df_columns]
    for kw in keywords:
        for col, col_low in zip(df_columns, lowered):
            if kw in col_low:
                return col
    return None

uploaded_file = st.file_uploader("Upload your dataset (CSV, XLS, XLSX)", type=["csv", "xls", "xlsx"])

if uploaded_file:
    df, file_format, encoding, error = read_dataset(uploaded_file)

    if error:
        st.error(f"Error reading file: {error}")
    elif df is not None:
        st.success(f"File loaded! Format: {file_format}, Encoding: {encoding}")

        # Detect columns dynamically
        brand_col = find_column(df.columns, ["brand", "company", "manufacturer", "make", "vendor"])
        mouse_name_col = find_column(df.columns, ["name", "mouse name", "product", "model"])
        type_col = find_column(df.columns, ["type", "category", "usage", "purpose"])

        # Ensure these columns exist with fallback values so filters work without errors
        if brand_col not in df.columns:
            df["Brand"] = "Unknown"
            brand_col = "Brand"
        if mouse_name_col not in df.columns:
            df["Mouse Name"] = "Unknown"
            mouse_name_col = "Mouse Name"
        if type_col not in df.columns:
            df["Type"] = "Unknown"
            type_col = "Type"

        if st.button("🎛️ Filters"):
            st.session_state.show_filters = not st.session_state.show_filters

        if st.session_state.show_filters:
            st.subheader("🧩 Choose Mouse Preferences")
            col1, col2, col3, col4 = st.columns([3, 3, 2, 2])

            with col1:
                brands = df[brand_col].dropna().unique().tolist()
                selected_brands = st.multiselect("Brand", options=brands, default=st.session_state.selected_brands)
                st.session_state.selected_brands = selected_brands

            with col2:
                mouse_names = df[mouse_name_col].dropna().unique().tolist()
                selected_mouse_names = st.multiselect("Mouse Name", options=mouse_names, default=st.session_state.selected_mouse_names)
                st.session_state.selected_mouse_names = selected_mouse_names

            with col3:
                mouse_types = ["", "Gaming", "Normal", "Design/Edit"]
                selected_type = st.selectbox("Mouse Type", options=mouse_types, index=mouse_types.index(st.session_state.type_option) if st.session_state.type_option in mouse_types else 0)
                st.session_state.type_option = selected_type

            with col4:
                st.markdown("### Choose wire type")
                wired_checked = st.checkbox("Wired", value=st.session_state.wired_checked)
                wireless_checked = st.checkbox("Wireless", value=st.session_state.wireless_checked)
                st.session_state.wired_checked = wired_checked
                st.session_state.wireless_checked = wireless_checked

            if st.button("Go"):
                st.session_state.filters_applied = True
                st.session_state.show_filters = False

        if st.session_state.filters_applied:
            st.subheader("🎯 Results")
            filtered_df = df.copy()

            # Apply filters if selected
            if st.session_state.selected_brands:
                filtered_df = filtered_df[filtered_df[brand_col].isin(st.session_state.selected_brands)]

            if st.session_state.selected_mouse_names:
                filtered_df = filtered_df[filtered_df[mouse_name_col].isin(st.session_state.selected_mouse_names)]

            if st.session_state.type_option and st.session_state.type_option != "":
                filtered_df = filtered_df[filtered_df[type_col] == st.session_state.type_option]

            # Wired/Wireless filter
            if st.session_state.wired_checked or st.session_state.wireless_checked:
                wire_mask = pd.Series([False] * len(filtered_df))
                # Check wired
                if st.session_state.wired_checked:
                    wire_mask = wire_mask | filtered_df.apply(lambda row: row.astype(str).str.lower().str.contains("wired").any(), axis=1)
                # Check wireless
                if st.session_state.wireless_checked:
                    wire_mask = wire_mask | filtered_df.apply(lambda row: row.astype(str).str.lower().str.contains("wireless").any(), axis=1)
                filtered_df = filtered_df[wire_mask]

            styled_df = filtered_df.reset_index(drop=True).style.set_table_styles([
                {'selector': 'th, td',
                 'props': [('border', '1px solid #ccc'),
                           ('padding', '6px'),
                           ('text-align', 'left')]}
            ]).set_properties(**{'border-collapse': 'collapse'})

            st.dataframe(styled_df, use_container_width=True)
