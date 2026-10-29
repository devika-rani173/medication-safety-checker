
import streamlit as st
import pandas as pd
import requests

# ---------------- PAGE SETTINGS ----------------
st.set_page_config(
    page_title="MediSafe - Medication Safety Checker",
    page_icon="💊",
    layout="wide"
)

# ---------------- BACKGROUND AND CSS ----------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #e8f8ef, #f7fbff, #e3f3ed);
}
.block-container {
    max-width: 1200px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}
h1, h2, h3 {
    color: #145844;
}
div[data-testid="stVerticalBlockBorderWrapper"] {
    background: rgba(255,255,255,0.94);
    border: 1px solid #d5eadd;
    border-radius: 18px;
}
.stButton > button {
    background-color: #16805d;
    color: white;
    border-radius: 10px;
    border: none;
    font-weight: bold;
}
.stButton > button:hover {
    background-color: #0d6045;
    color: white;
}
</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.markdown("""
<div style="
    background: linear-gradient(120deg, #124e40, #27966f);
    padding: 30px;
    border-radius: 22px;
    color: white;
    margin-bottom: 22px;">
    <h1 style="color:white;">💊 MediSafe</h1>
    <h3 style="color:#d8ffeb;">Your Medicines. Your Safety.</h3>
    <p style="font-size:17px;">
    Check documented medicine interactions and explore
    available medicine-label information.
    </p>
</div>
""", unsafe_allow_html=True)

# ---------------- MEDICINE PHOTOS ----------------
st.subheader("Your Health, Our Priority")

col1, col2, col3 = st.columns(3)

with col1:
    st.image(
        "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?auto=format&fit=crop&w=700&q=80",
        caption="Medicines and healthcare",
        use_container_width=True
    )

with col2:
    st.image(
        "https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?auto=format&fit=crop&w=700&q=80",
        caption="Healthcare professionals",
        use_container_width=True
    )

with col3:
    st.image(
        "https://images.unsplash.com/photo-1559757175-0eb30cd8c063?auto=format&fit=crop&w=700&q=80",
        caption="Health and wellness",
        use_container_width=True
    )

st.divider()

# ---------------- LOAD INTERACTION DATASET ----------------
@st.cache_data
def load_data():
    return pd.read_csv("ddinter_downloads_code_A.csv")

try:
    df = load_data()
    required_columns = {"Drug_A", "Drug_B", "Level"}

    if not required_columns.issubset(df.columns):
        st.error("The interaction CSV does not contain the required columns.")
        st.stop()

except FileNotFoundError:
    st.error(
        "Dataset not found. Keep ddinter_downloads_code_A.csv "
        "in the same folder as app.py."
    )
    st.stop()

# ---------------- TABS ----------------
tab1, tab2, tab3 = st.tabs([
    "💊 Interaction Checker",
    "🔎 Medicine Information",
    "ℹ️ About MediSafe"
])

# ---------------- TAB 1: INTERACTION CHECKER ----------------
with tab1:
    st.header("Check Medicine Interactions")
    st.write("Select two medicines to check the available interaction records.")

    with st.container(border=True):
        medicines = sorted(set(
            df["Drug_A"].dropna().astype(str).str.strip().tolist()
            + df["Drug_B"].dropna().astype(str).str.strip().tolist()
        ))
        medicines = [m for m in medicines if m]

        drug1 = st.selectbox(
            "Select the first medicine",
            medicines,
            key="drug1"
        )

        drug2 = st.selectbox(
            "Select the second medicine",
            medicines,
            index=1 if len(medicines) > 1 else 0,
            key="drug2"
        )

        if st.button("Check Interaction", key="check_interaction"):
            if drug1.casefold() == drug2.casefold():
                st.warning("Please select two different medicines.")
            else:
                match = df[
                    (
                        (df["Drug_A"].str.casefold() == drug1.casefold())
                        & (df["Drug_B"].str.casefold() == drug2.casefold())
                    )
                    |
                    (
                        (df["Drug_A"].str.casefold() == drug2.casefold())
                        & (df["Drug_B"].str.casefold() == drug1.casefold())
                    )
                ]

                if not match.empty:
                    levels = match["Level"].dropna().astype(str).unique()

                    st.subheader("Interaction record found")

                    for level in levels:
                        if level.casefold() == "major":
                            st.error("Major interaction recorded")
                        elif level.casefold() == "moderate":
                            st.warning("Moderate interaction recorded")
                        elif level.casefold() == "minor":
                            st.info("Minor interaction recorded")
                        else:
                            st.write("Recorded level:", level)

                    st.dataframe(
                        match[["Drug_A", "Drug_B", "Level"]]
                        .drop_duplicates(),
                        use_container_width=True,
                        hide_index=True
                    )

                    st.warning(
                        "This is a database result, not a personalized "
                        "medical assessment. Ask a doctor or pharmacist "
                        "before combining medicines."
                    )
                else:
                    st.info(
                        "No interaction record was found for this pair "
                        "in the available dataset. This does NOT mean "
                        "the combination is safe."
                    )

# ---------------- TAB 2: FDA MEDICINE INFORMATION ----------------
with tab2:
    st.header("Medicine Label Information")
    st.write(
        "Search for available medicine-label information from the "
        "US FDA open data service."
    )

    medicine_name = st.text_input(
        "Enter a generic or brand medicine name",
        placeholder="Example: paracetamol"
    )

    if st.button("Search Medicine", key="search_medicine"):
        if not medicine_name.strip():
            st.warning("Please enter a medicine name.")
        else:
            with st.spinner("Searching medicine information..."):
                try:
                    url = "https://api.fda.gov/drug/label.json"
                    params = {
                        "search": (
                            f'openfda.generic_name:"{medicine_name}" '
                            f'OR openfda.brand_name:"{medicine_name}"'
                        ),
                        "limit": 1
                    }

                    response = requests.get(
                        url, params=params, timeout=15
                    )

                    if response.status_code == 200:
                        results = response.json().get("results", [])

                        if results:
                            result = results[0]
                            openfda = result.get("openfda", {})

                            st.success("Medicine label information found")

                            brands = openfda.get("brand_name", [])
                            generics = openfda.get("generic_name", [])

                            if brands:
                                st.write("**Brand name:**", ", ".join(brands))
                            if generics:
                                st.write("**Generic name:**", ", ".join(generics))

                            sections = [
                                ("drug_interactions", "Drug Interactions"),
                                ("warnings", "Warnings"),
                                ("warnings_and_cautions", "Warnings and Cautions"),
                                ("precautions", "Precautions"),
                                ("contraindications", "Contraindications")
                            ]

                            found_section = False

                            for key, title in sections:
                                content = result.get(key, [])

                                if content:
                                    found_section = True
                                    with st.expander(title, expanded=(key == "drug_interactions")):
                                        st.write("\n\n".join(content))

                            if not found_section:
                                st.info(
                                    "The returned label does not contain "
                                    "the selected information sections."
                                )

                            st.caption(
                                "Label information may be incomplete or "
                                "not apply to your individual situation."
                            )
                        else:
                            st.info(
                                "No matching FDA label was found. Try another "
                                "spelling or the generic medicine name."
                            )

                    elif response.status_code == 404:
                        st.info("No matching medicine label was found.")
                    else:
                        st.error(
                            "The medicine information service returned "
                            f"status code {response.status_code}."
                        )

                except requests.RequestException:
                    st.error(
                        "Could not connect to the FDA service. Check your "
                        "internet connection and try again."
                    )
                except ValueError:
                    st.error("The service returned an unreadable response.")

# ---------------- TAB 3: ABOUT ----------------
with tab3:
    st.header("About MediSafe")
    st.write("""
    MediSafe is an educational project designed to help users explore
    documented medicine interactions and publicly available medicine-label
    information.

    **Features**
    - Medicine interaction lookup using the DDInter dataset.
    - Medicine-label search using the US FDA open data service.
    - A simple, user-friendly healthcare interface.
    - Warnings when information is missing or incomplete.
    """)

    st.info(
        "Dataset limitation: this project uses a particular DDInter "
        "dataset file, so it does not cover every medicine or interaction."
    )

# ---------------- FOOTER ----------------
st.divider()
st.caption(
    "⚕️ Educational project only. MediSafe does not diagnose, prescribe, "
    "or replace advice from a qualified doctor or pharmacist. "
    "Never start, stop, or combine medicines based only on this app."
)
