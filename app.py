import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="E-Commerce Conversion Analytics", layout="wide")

@st.cache_data
def load_data():
    from ucimlrepo import fetch_ucirepo
    ds = fetch_ucirepo(id=468)
    df = pd.concat([ds.data.features.copy(), ds.data.targets.copy()], axis=1)
    df["Revenue"] = df["Revenue"].astype(str).str.lower().isin(["true","1","yes"])
    df["Weekend"] = df["Weekend"].astype(str).str.lower().isin(["true","1","yes"])
    df["Visitor_Group"] = df["VisitorType"].replace({
        "Returning_Visitor":"Returning Visitor",
        "New_Visitor":"New Visitor",
        "Other":"Other"
    })
    return df

df = load_data()

st.title("E-Commerce Purchase Conversion Analytics")
st.caption("Business dashboard built from the UCI Online Shoppers Purchasing Intention Dataset")

with st.sidebar:
    st.header("Filters")
    visitor = st.multiselect("Visitor Type", sorted(df["Visitor_Group"].unique()),
                             default=sorted(df["Visitor_Group"].unique()))
    months = st.multiselect("Month", sorted(df["Month"].unique()),
                            default=sorted(df["Month"].unique()))

f = df[df["Visitor_Group"].isin(visitor) & df["Month"].isin(months)].copy()

sessions = len(f)
purchases = int(f["Revenue"].sum())
conversion = purchases / sessions * 100 if sessions else 0
avg_page_value = f["PageValues"].mean() if sessions else 0

c1,c2,c3,c4 = st.columns(4)
c1.metric("Sessions", f"{sessions:,}")
c2.metric("Purchases", f"{purchases:,}")
c3.metric("Conversion Rate", f"{conversion:.2f}%")
c4.metric("Avg Page Value", f"{avg_page_value:.2f}")

left, right = st.columns(2)

with left:
    v = f.groupby("Visitor_Group", as_index=False)["Revenue"].mean()
    v["Conversion Rate"] = v["Revenue"] * 100
    fig = px.bar(v, x="Visitor_Group", y="Conversion Rate",
                 title="Conversion Rate by Visitor Type",
                 labels={"Visitor_Group":"Visitor Type"})
    st.plotly_chart(fig, use_container_width=True)

with right:
    m = f.groupby("Month", as_index=False)["Revenue"].mean()
    m["Conversion Rate"] = m["Revenue"] * 100
    fig = px.bar(m, x="Month", y="Conversion Rate",
                 title="Conversion Rate by Month")
    st.plotly_chart(fig, use_container_width=True)

left, right = st.columns(2)

with left:
    w = f.groupby("Weekend", as_index=False)["Revenue"].mean()
    w["Visit Timing"] = w["Weekend"].map({True:"Weekend", False:"Weekday"})
    w["Conversion Rate"] = w["Revenue"] * 100
    fig = px.bar(w, x="Visit Timing", y="Conversion Rate",
                 title="Weekday vs Weekend Conversion")
    st.plotly_chart(fig, use_container_width=True)

with right:
    f["Page Value Band"] = pd.cut(
        f["PageValues"], [-0.001,0,5,20,50,float("inf")],
        labels=["0","0–5","5–20","20–50","50+"]
    )
    p = f.groupby("Page Value Band", observed=False, as_index=False)["Revenue"].mean()
    p["Conversion Rate"] = p["Revenue"] * 100
    fig = px.bar(p, x="Page Value Band", y="Conversion Rate",
                 title="Conversion Rate by Page Value Band")
    st.plotly_chart(fig, use_container_width=True)

st.subheader("Business Interpretation")
st.markdown("""
- **Conversion:** Monitor conversion rate as the primary outcome KPI.
- **Visitor segments:** Compare new and returning visitors to identify retention and acquisition opportunities.
- **Engagement:** Product-related page activity and time can be used to identify high-engagement sessions.
- **Page value:** Sessions with stronger page-value signals can be prioritized for conversion-focused experiences.
- **Timing:** Month and weekday/weekend patterns can support campaign scheduling and staffing decisions.
- **Action:** Use the dashboard as a decision-support layer rather than relying on a single metric.
""")
