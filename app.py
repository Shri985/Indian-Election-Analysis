import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# PAGE CONFIG
st.set_page_config(
    page_title="Indian General Elections Dashboard",
    page_icon="🗳️",
    layout="wide"
)

# STYLING
st.markdown("""
<style>
.main {background-color: #0f172a;}
h1, h2, h3 {color: #e5e7eb;}
label {color: #e5e7eb;}
.stMetric {
    background-color: #020617;
    padding: 12px;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

# HELPERS
def normalize(df):
    df.columns = (
        df.columns.str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace(".", "_")
    )
    return df


def map_semantic(df):
    rename = {}

    for c in df.columns:
        if c in ["state", "state_name"]:
            rename[c] = "state"
        elif c in ["party", "party_name"]:
            rename[c] = "party"
        elif c in ["votes", "total_votes", "valid_votes"]:
            rename[c] = "votes"
        elif c in ["margin", "vote_margin", "winning_margin"]:
            rename[c] = "margin"

    return df.rename(columns=rename)


def has(df, col):
    return col in df.columns

# LOAD DATA (NO INTERSECTION, NO ASSUMPTIONS)
@st.cache_data
def load_data():
    d14 = map_semantic(normalize(pd.read_csv("india_election_2014.csv")))
    d19 = map_semantic(normalize(pd.read_csv("india_election_2019.csv")))
    d24 = pd.read_csv("election_results_2024.csv")


    if "Margin" in d24.columns:
        d24["Margin"] = pd.to_numeric(d24["Margin"], errors="coerce")
        d24 = d24.dropna(subset=["Margin"])

    
    d24 = map_semantic(normalize(d24))


    d14["year"] = 2014
    d19["year"] = 2019
    d24["year"] = 2024

    return pd.concat([d14, d19, d24], ignore_index=True, sort=False)


df = load_data()

# SIDEBAR CONTROLS
st.sidebar.title("🎛 Dashboard Controls")

year = st.sidebar.selectbox(
    "Election Year",
    sorted(df["year"].unique())
)

filtered = df[df["year"] == year]

# STATE FILTER
if has(filtered, "state"):
    state = st.sidebar.selectbox(
        "State",
        ["All"] + sorted(filtered["state"].dropna().unique())
    )
    if state != "All":
        filtered = filtered[filtered["state"] == state]
else:
    st.sidebar.info("ℹ️ State data not available")

# PARTY FILTER
if has(filtered, "party"):
    party = st.sidebar.selectbox(
        "Party",
        ["All"] + sorted(filtered["party"].dropna().unique())
    )
    if party != "All":
        filtered = filtered[filtered["party"] == party]
else:
    st.sidebar.info("ℹ️ Party data not available")

# HEADER
st.title("🗳️ Indian General Elections Analytics Dashboard")
st.markdown("### Fully Schema-Adaptive")

# KPIs
c1, c2, c3, c4 = st.columns(4)

c1.metric("Records", filtered.shape[0])

if has(filtered, "party"):
    c2.metric("Parties", filtered["party"].nunique())
else:
    c2.metric("Parties", "N/A")

if has(filtered, "votes"):
    votes_numeric = pd.to_numeric(filtered["votes"], errors="coerce")
    avg_votes = votes_numeric.dropna().mean()

    if pd.notna(avg_votes):
        c3.metric("Avg Votes", int(avg_votes))
    else:
        c3.metric("Avg Votes", "N/A")
else:
    c3.metric("Avg Votes", "N/A")

if has(filtered, "margin"):
    margin_numeric = pd.to_numeric(filtered["margin"], errors="coerce")
    avg_margin = margin_numeric.dropna().mean()

    if pd.notna(avg_margin):
        c4.metric("Avg Margin", int(avg_margin))
    else:
        c4.metric("Avg Margin", "N/A")
else:
    c4.metric("Avg Margin", "N/A")

# PARTY DISTRIBUTION
if has(filtered, "party"):
    st.markdown("## 🏆 Party-wise Distribution")

    fig = plt.figure()
    filtered["party"].value_counts().head(10).plot(kind="bar")
    plt.xlabel("Party")
    plt.ylabel("Count")
    plt.title("Top Parties")
    st.pyplot(fig)

# VOTES DISTRIBUTION
if has(filtered, "votes"):
    st.markdown("## 📊 Votes Distribution")

    fig = plt.figure()
    plt.hist(filtered["votes"], bins=30)
    plt.xlabel("Votes")
    plt.ylabel("Frequency")
    plt.title("Votes Histogram")
    st.pyplot(fig)

# MARGIN DISTRIBUTION
if has(filtered, "margin"):
    st.markdown("## ⚔️ Margin of Victory")

    fig = plt.figure()
    plt.hist(filtered["margin"], bins=40)
    plt.xlabel("Margin")
    plt.ylabel("Constituencies")
    plt.title("Winning Margin")
    st.pyplot(fig)

# STATE DISTRIBUTION
if has(filtered, "state"):
    st.markdown("## 🗺️ State-wise Contribution")

    fig = plt.figure()
    filtered["state"].value_counts().head(10).plot(kind="bar")
    plt.xlabel("State")
    plt.ylabel("Count")
    plt.title("Top States")
    st.pyplot(fig)

# DATA PREVIEW
st.markdown("## 📄 Data Preview")
st.dataframe(filtered.head(20))

# FOOTER
st.markdown("---")
st.markdown(
    "<center>Created by Shashank Shrivastava • Exploratory Data Analysis Project</center>",
    unsafe_allow_html=True
)