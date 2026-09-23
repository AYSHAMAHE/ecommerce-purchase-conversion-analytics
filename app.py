import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(
    page_title="E-Commerce Purchase Conversion Analytics",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------
# Professional dashboard styling
# -----------------------------
st.markdown(
    """
    <style>
    .stApp { background: #f4f7fb; }
    [data-testid="stHeader"] { background: rgba(244,247,251,.92); }
    .block-container { max-width: 1450px; padding-top: 1.4rem; padding-bottom: 3rem; }

    .hero {
        background: linear-gradient(120deg, #102a43 0%, #1769aa 52%, #00a6a6 100%);
        border-radius: 20px;
        padding: 30px 34px;
        margin-bottom: 22px;
        box-shadow: 0 12px 30px rgba(16,42,67,.18);
        position: relative;
        overflow: hidden;
    }
    .hero:after {
        content: "";
        position: absolute;
        width: 230px; height: 230px;
        border-radius: 50%;
        right: -70px; top: -95px;
        background: rgba(255,255,255,.10);
    }
    .hero h1 { color:#fff; margin:0; font-size:2.25rem; font-weight:800; letter-spacing:-.5px; }
    .hero p { color:rgba(255,255,255,.88); margin:8px 0 0; font-size:1rem; }
    .hero .tag { display:inline-block; margin-top:15px; padding:6px 11px; border-radius:20px; background:rgba(255,255,255,.15); color:#fff; font-size:.78rem; font-weight:650; }

    .section-title { color:#102a43; font-size:1.35rem; font-weight:800; margin:18px 0 12px; }
    .section-subtitle { color:#667085; font-size:.9rem; margin:-5px 0 14px; }

    .kpi-card {
        background:#fff; border-radius:16px; padding:18px 20px; min-height:116px;
        border:1px solid #e5eaf1; box-shadow:0 7px 22px rgba(16,42,67,.07);
        position:relative; overflow:hidden;
    }
    .kpi-card:before { content:""; position:absolute; left:0; top:0; bottom:0; width:5px; background:var(--accent); }
    .kpi-icon { font-size:1.35rem; }
    .kpi-label { color:#667085; font-size:.82rem; font-weight:700; margin-top:6px; }
    .kpi-value { color:#102a43; font-size:1.85rem; font-weight:800; margin-top:3px; }
    .kpi-note { color:#98a2b3; font-size:.73rem; margin-top:2px; }

    .chart-card { background:#fff; border:1px solid #e5eaf1; border-radius:16px; padding:5px 8px 0; box-shadow:0 7px 22px rgba(16,42,67,.055); }

    .insight-card {
        background:#fff; border:1px solid #e5eaf1; border-radius:15px; padding:17px 18px;
        min-height:145px; box-shadow:0 6px 18px rgba(16,42,67,.055); border-top:4px solid var(--accent);
    }
    .insight-card .icon { font-size:1.35rem; }
    .insight-card h4 { color:#102a43; margin:6px 0 6px; font-size:1rem; }
    .insight-card p { color:#667085; margin:0; line-height:1.48; font-size:.87rem; }

    [data-testid="stSidebar"] { background:linear-gradient(180deg,#102a43 0%,#173f5f 100%); }
    [data-testid="stSidebar"] * { color:#fff !important; }
    [data-testid="stSidebar"] .stCaption { color:#c9d6e2 !important; }
    [data-testid="stSidebar"] hr { border-color:rgba(255,255,255,.18); }
    [data-testid="stSidebar"] [data-baseweb="select"] > div { background:#fff; color:#102a43; border-radius:10px; }
    [data-testid="stSidebar"] [data-baseweb="select"] * { color:#102a43 !important; }

    .footer-note { text-align:center; color:#98a2b3; font-size:.78rem; margin-top:30px; padding-top:16px; border-top:1px solid #e5eaf1; }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data
def load_data():
    from ucimlrepo import fetch_ucirepo

    ds = fetch_ucirepo(id=468)
    df = pd.concat([ds.data.features.copy(), ds.data.targets.copy()], axis=1)
    df["Revenue"] = df["Revenue"].astype(str).str.lower().isin(["true", "1", "yes"])
    df["Weekend"] = df["Weekend"].astype(str).str.lower().isin(["true", "1", "yes"])
    df["Visitor_Group"] = df["VisitorType"].replace(
        {"Returning_Visitor": "Returning Visitor", "New_Visitor": "New Visitor", "Other": "Other"}
    )
    return df


df = load_data()

# -----------------------------
# Header
# -----------------------------
st.markdown(
    """
    <div class="hero">
        <h1>🛒 E-Commerce Purchase Conversion Analytics</h1>
        <p>Interactive business intelligence dashboard for understanding online shopping conversion behavior.</p>
        <span class="tag">UCI Online Shoppers Purchasing Intention Dataset</span>
    </div>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# Sidebar filters
# -----------------------------
with st.sidebar:
    st.markdown("# 🎛️ Dashboard Filters")
    st.caption("Explore conversion behavior by visitor segment and month.")
    st.divider()

    visitor_options = ["All Visitor Types"] + sorted(df["Visitor_Group"].unique().tolist())
    month_options = ["All Months"] + sorted(df["Month"].unique().tolist())

    visitor_choice = st.selectbox("Visitor Type", visitor_options, index=0)
    month_choice = st.selectbox("Month", month_options, index=0)

    st.divider()
    st.markdown("### 📌 Dashboard Focus")
    st.caption("• Conversion performance")
    st.caption("• Visitor segments")
    st.caption("• Timing patterns")
    st.caption("• Page-value signals")

    st.divider()
    st.caption("Dataset: UCI Online Shoppers Purchasing Intention")

f = df.copy()
if visitor_choice != "All Visitor Types":
    f = f[f["Visitor_Group"] == visitor_choice]
if month_choice != "All Months":
    f = f[f["Month"] == month_choice]

# -----------------------------
# KPI cards
# -----------------------------
sessions = len(f)
purchases = int(f["Revenue"].sum())
conversion = purchases / sessions * 100 if sessions else 0
avg_page_value = f["PageValues"].mean() if sessions else 0

st.markdown('<div class="section-title">📌 Executive Overview</div>', unsafe_allow_html=True)
st.markdown('<div class="section-subtitle">Key performance indicators for the selected view</div>', unsafe_allow_html=True)

kpis = [
    ("👥", "Sessions", f"{sessions:,}", "Total shopping sessions", "#1769aa"),
    ("🛍️", "Purchases", f"{purchases:,}", "Completed purchase sessions", "#00a6a6"),
    ("📈", "Conversion Rate", f"{conversion:.2f}%", "Purchase rate across sessions", "#f28e2b"),
    ("💰", "Avg Page Value", f"{avg_page_value:.2f}", "Average page-value signal", "#7b61a8"),
]
cols = st.columns(4, gap="medium")
for col, (icon, label, value, note, accent) in zip(cols, kpis):
    with col:
        st.markdown(
            f"""
            <div class="kpi-card" style="--accent:{accent}">
                <div class="kpi-icon">{icon}</div>
                <div class="kpi-label">{label}</div>
                <div class="kpi-value">{value}</div>
                <div class="kpi-note">{note}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# -----------------------------
# Chart helper
# -----------------------------
def polish(fig, title, y_title="Conversion Rate (%)"):
    fig.update_traces(
        texttemplate="%{text:.1f}%",
        textposition="outside",
        cliponaxis=False,
        marker_line_width=0,
    )
    fig.update_layout(
        title=dict(text=title, font=dict(size=17, color="#102a43"), x=0.02, xanchor="left"),
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(color="#475467", family="Arial"),
        margin=dict(l=40, r=25, t=62, b=45),
        height=365,
        xaxis=dict(showgrid=False, title="", linecolor="#e5eaf1"),
        yaxis=dict(showgrid=True, gridcolor="#edf1f5", title=y_title, zeroline=False),
        hoverlabel=dict(bgcolor="#102a43", font_color="white"),
    )
    return fig


st.markdown('<div class="section-title">📊 Conversion Performance</div>', unsafe_allow_html=True)
st.markdown('<div class="section-subtitle">Compare conversion across customer segments and time periods</div>', unsafe_allow_html=True)

left, right = st.columns(2, gap="large")

with left:
    v = f.groupby("Visitor_Group", as_index=False)["Revenue"].mean()
    v["Conversion Rate"] = v["Revenue"] * 100
    fig = px.bar(v, x="Visitor_Group", y="Conversion Rate", text="Conversion Rate",
                 color="Visitor_Group", color_discrete_sequence=["#1769aa", "#00a6a6", "#f28e2b"])
    fig = polish(fig, "Conversion Rate by Visitor Type")
    with st.container(border=True):
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

with right:
    m = f.groupby("Month", as_index=False)["Revenue"].mean()
    m["Conversion Rate"] = m["Revenue"] * 100
    fig = px.bar(m, x="Month", y="Conversion Rate", text="Conversion Rate", color="Conversion Rate",
                 color_continuous_scale=[[0,"#d8eff7"],[0.55,"#1769aa"],[1,"#00a6a6"]])
    fig = polish(fig, "Conversion Rate by Month")
    fig.update_coloraxes(showscale=False)
    with st.container(border=True):
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

left, right = st.columns(2, gap="large")

with left:
    w = f.groupby("Weekend", as_index=False)["Revenue"].mean()
    w["Visit Timing"] = w["Weekend"].map({True: "Weekend", False: "Weekday"})
    w["Conversion Rate"] = w["Revenue"] * 100
    fig = px.bar(w, x="Visit Timing", y="Conversion Rate", text="Conversion Rate",
                 color="Visit Timing", color_discrete_sequence=["#7b61a8", "#f28e2b"])
    fig = polish(fig, "Weekday vs Weekend Conversion")
    with st.container(border=True):
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

with right:
    f = f.copy()

    bands = ["0", "0-5", "5-20", "20-50", "50+"]

    f["Page Value Band"] = pd.cut(
        f["PageValues"],
        bins=[-0.001, 0, 5, 20, 50, float("inf")],
        labels=bands,
        include_lowest=True
    )

    p = (
        f.groupby("Page Value Band", observed=False)["Revenue"]
        .mean()
        .reindex(bands)
        .reset_index()
    )

    p["Conversion Rate"] = p["Revenue"] * 100
    p["x"] = list(range(len(bands)))

    fig = px.bar(
        p,
        x="x",
        y="Conversion Rate",
        text="Conversion Rate",
        color="Page Value Band",
        color_discrete_sequence=[
            "#b8c4d6",
            "#7aaed6",
            "#4e91c6",
            "#1769aa",
            "#00a6a6"
        ]
    )

    fig = polish(fig, "Conversion Rate by Page Value Band")

    fig.update_traces(
        texttemplate="%{text:.1f}%",
        textposition="outside"
    )

    fig.update_xaxes(
        tickmode="array",
        tickvals=[0, 1, 2, 3, 4],
        ticktext=bands,
        title="Page Value Band"
    )

    fig.update_layout(
        showlegend=False,
        yaxis=dict(range=[0, 100])
    )

    with st.container(border=True):
        st.plotly_chart(
            fig,
            use_container_width=True,
            config={"displayModeBar": False}
        )
# -----------------------------
# Business insights
# -----------------------------
st.markdown('<div class="section-title">💡 Business Interpretation & Actions</div>', unsafe_allow_html=True)
st.markdown('<div class="section-subtitle">How the observed patterns can support business decisions</div>', unsafe_allow_html=True)

insights = [
    ("🎯", "Conversion", "Track conversion rate as the primary outcome KPI and use it to evaluate changes in shopping behavior.", "#1769aa"),
    ("👥", "Visitor Segments", "Compare new and returning visitors to identify acquisition and retention opportunities.", "#00a6a6"),
    ("📈", "Engagement", "Use product-related page activity and time to identify high-engagement shopping sessions.", "#f28e2b"),
    ("💰", "Page Value", "Prioritize sessions with stronger page-value signals for conversion-focused experiences.", "#7b61a8"),
    ("📅", "Timing", "Use monthly and weekday/weekend patterns to support campaign scheduling and staffing decisions.", "#1769aa"),
    ("🚀", "Action", "Use the dashboard as a decision-support layer rather than relying on a single metric.", "#00a6a6"),
]

for start in range(0, len(insights), 3):
    cols = st.columns(3, gap="medium")
    for col, (icon, title, body, accent) in zip(cols, insights[start:start+3]):
        with col:
            st.markdown(
                f"""
                <div class="insight-card" style="--accent:{accent}">
                    <div class="icon">{icon}</div>
                    <h4>{title}</h4>
                    <p>{body}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

st.markdown(
    '<div class="footer-note">E-Commerce Purchase Conversion Analytics • Data Analytics with AI Internship Project</div>',
    unsafe_allow_html=True,
)
