import streamlit as st
import pandas as pd
import re
from shared.data_reader import read_dataset

st.set_page_config(page_title="🖱️ Mouse Decision Maker", layout="wide")
st.title("🖱️ Mouse Decision Maker")

# Session state
if "show_filters" not in st.session_state:
    st.session_state.show_filters = True
if "type_option" not in st.session_state:
    st.session_state.type_option = ""
if "subtype_option" not in st.session_state:
    st.session_state.subtype_option = ""

# Upload section
uploaded_file = st.file_uploader("Upload your dataset (CSV, XLS, XLSX)", type=["csv", "xls", "xlsx"])

if uploaded_file:
    df, file_format, encoding, error = read_dataset(uploaded_file)

    if error:
        st.error(f"Error reading file: {error}")
    elif df is not None:
        st.success(f"File loaded! Format: {file_format}, Encoding: {encoding}")

        if df.shape[1] == 1:
            df = df[df.columns[0]].str.split(";", expand=True)

        if any(str(col).startswith("Unnamed") for col in df.columns):
            df.columns = df.iloc[0]
            df = df[1:]

        df.columns = df.columns.astype(str).str.strip()

        if st.button("🎛️ Filters"):
            st.session_state.show_filters = not st.session_state.show_filters

        if st.session_state.show_filters:
            st.subheader("🧩 Choose Mouse Preferences")
            colA, colB = st.columns([3, 2])

            with colA:
                # Brand
                if 'Brand' in df.columns:
                    brand_options = df['Brand'].dropna().unique().tolist()
                else:
                    brand_options = ["Logitech", "Razer", "Corsair", "Pulsar", "Others"]
                st.multiselect("Brand", options=brand_options)

                # Mouse Type
                st.session_state.type_option = st.selectbox(
                    "Mouse Type", ["", "Gaming", "Normal", "Design/Edit"],
                    index=["", "Gaming", "Normal", "Design/Edit"].index(st.session_state.type_option)
                )

                # Subtype
                if st.session_state.type_option == "Gaming":
                    st.session_state.subtype_option = st.radio(
                        "Subtype", ["Casual", "Hard-core"],
                        index=0 if st.session_state.subtype_option == "" else ["Casual", "Hard-core"].index(st.session_state.subtype_option),
                        horizontal=True
                    )

                # Connectivity as checkbox
                if 'Connectivity' in df.columns:
                    connectivity_options = df['Connectivity'].dropna().unique().tolist()
                else:
                    connectivity_options = ["Wired", "Wireless", "Both"]
                selected_connectivity = {
                    opt: st.checkbox(opt, value=False) for opt in connectivity_options
                }

            with colB:
                # Hand Compatibility
                if "Hand compatibility" in df.columns:
                    hand_options = df["Hand compatibility"].dropna().unique().tolist()
                else:
                    hand_options = ["Right", "Left", "Ambidextrous"]
                st.selectbox("Hand Compatibility", [""] + hand_options)

                # Button Count Slider
                default_min, default_max = 2, 10
                side_button_col = "Side buttons"
                middle_button_col = "Middle buttons"

                if side_button_col in df.columns and pd.api.types.is_numeric_dtype(df[side_button_col]):
                    min_val, max_val = int(df[side_button_col].min()), int(df[side_button_col].max())
                    st.slider(f"{side_button_col}", min_val, max_val, min_val)
                else:
                    st.slider("Side Buttons", default_min, default_max, default_min)

                if middle_button_col in df.columns and pd.api.types.is_numeric_dtype(df[middle_button_col]):
                    min_val, max_val = int(df[middle_button_col].min()), int(df[middle_button_col].max())
                    st.slider(f"{middle_button_col}", min_val, max_val, min_val)
                else:
                    st.slider("Middle Buttons", 0, 3, 0)

                # DPI
                dpi_range = (400, 32000)
                st.slider("Preferred DPI Range", dpi_range[0], dpi_range[1], (800, 1600))

                # Polling Rate
                st.selectbox("Polling Rate", [125, 500, 1000, 4000, 8000])

                # Sensor Tech
                st.selectbox("Sensor Technology", ["Optical", "Laser", "Hybrid"])

        # Data display
        st.subheader("📊 Uploaded Table")
        st.dataframe(df.reset_index(drop=True), use_container_width=True)
