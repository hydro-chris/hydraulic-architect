import streamlit as st
import pandas as pd
import os

# 1. Page Configuration
st.set_page_config(page_title="Hydraulic Architect", layout="wide", initial_sidebar_state="expanded")

# Custom CSS to make it look professional
st.markdown("""
    <style>
    .main { background-color: #1e1e26; color: white; }
    .stSelectbox label { color: #ff3333 !important; font-weight: bold; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #2c3e50; color: white; }
    </style>
    """, unsafe_allow_html=True)

# 2. Load Data
@st.cache_data
def load_data():
    if not os.path.exists("pumps.csv"):
        return None
    df = pd.read_csv("pumps.csv").fillna("N/A")
    df.columns = [str(c).strip().upper() for c in df.columns]
    return df.apply(lambda col: col.map(lambda x: str(x).strip().upper()))

df = load_data()

# 3. Sidebar: The Selection Wizard
with st.sidebar:
    st.sidebar.image("main_bg.jpg", use_column_width=True)
    st.title("Selection Wizard")
    if st.button("🔄 NEW SEARCH / RESET"):
        st.rerun()

    if df is not None:
        # Step 1: Category
        cat = st.radio("SELECT CATEGORY:", ["BEARING", "BUSHING"], index=None)
        
        if cat:
            active_df = df[df["CATEGORY"].str.contains(cat)].copy()
            
            # Iterative Search Logic
            skipped_cols = []
            found = False
            
            while len(active_df) > 1:
                # Find next distinguishing column
                next_col = None
                for col in active_df.columns:
                    if col not in ["CATEGORY", "SERIES"] and col not in skipped_cols:
                        if len(active_df[col].unique()) > 1:
                            next_col = col
                            break
                
                if next_col:
                    opts = sorted([str(v) for v in active_df[next_col].unique()]) + ["UNKNOWN / SKIP"]
                    selection = st.selectbox(f"IDENTIFY {next_col}:", opts, index=None, key=next_col)
                    
                    if selection == "UNKNOWN / SKIP":
                        skipped_cols.append(next_col)
                    elif selection:
                        active_df = active_df[active_df[next_col] == selection]
                    else:
                        break # Wait for user input
                else:
                    break

            # Result Logic
            if len(active_df) == 1:
                st.success(f"MATCH: {active_df.iloc[0]['SERIES']}")
                match_data = active_df.iloc[0]
            elif len(active_df) > 1:
                st.info(f"{len(active_df)} Possible Series remain.")
    else:
        st.error("pumps.csv not found!")

# 4. Main Area: Measurement Guides & Results
col1, col2 = st.columns([1, 2])

with col1:
    st.header("Results")
    if 'match_data' in locals():
        st.dataframe(match_data.drop(["CATEGORY", "SERIES"]), height=500)
    else:
        st.write("Complete the wizard on the left to see specs.")

with col2:
    st.header("Measurement Guides")
    img_folder = "images"
    if os.path.exists(img_folder):
        imgs = [f for f in os.listdir(img_folder) if f.lower().endswith(('.png', '.jpg')) and "main_bg" not in f]
        grid = st.columns(2)
        for i, img in enumerate(imgs):
            with grid[i % 2]:
                st.image(os.path.join(img_folder, img), caption=img.split(".")[0].upper())

st.markdown("---")
st.header("📚 Technical Reference & Formulas")
f_col1, f_col2 = st.columns(2)
with f_col1:
    st.latex(r"Flow (GPM) = \frac{Displacement \times RPM \times \text{Efficiency}}{231}")
with f_col2:
    st.latex(r"HP = \frac{PSI \times GPM}{1714 \times \text{Efficiency}}")
