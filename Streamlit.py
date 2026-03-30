import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ─── PAGE CONFIG ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Quick Commerce Analytics",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CUSTOM CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;600;700&display=swap');

:root {
    --bg-primary:    #0a0f0a;
    --bg-card:       #0f1a0f;
    --bg-card2:      #111c11;
    --green-1:       #00ff88;
    --green-2:       #00cc6a;
    --green-3:       #00994f;
    --green-4:       #006633;
    --green-5:       #003d1f;
    --text-primary:  #e8f5e9;
    --text-muted:    #6b8f72;
    --border:        #1a2e1a;
    --glow:          0 0 20px rgba(0,255,136,0.15);
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: var(--bg-primary) !important;
    color: var(--text-primary) !important;
}

/* ── Main background ── */
.stApp { background: var(--bg-primary) !important; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0a140a 0%, #0c1a0c 100%) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * { color: var(--text-primary) !important; }

/* ── Metric cards ── */
[data-testid="stMetric"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--green-5) !important;
    border-radius: 12px !important;
    padding: 18px !important;
    box-shadow: var(--glow) !important;
    transition: transform .2s ease, box-shadow .2s ease;
}
[data-testid="stMetric"]:hover {
    transform: translateY(-3px);
    box-shadow: 0 0 30px rgba(0,255,136,0.25) !important;
}
[data-testid="stMetricLabel"]  { color: var(--text-muted)   !important; font-size: .78rem !important; letter-spacing: .08em !important; text-transform: uppercase; }
[data-testid="stMetricValue"]  { color: var(--green-1)      !important; font-family: 'Space Mono', monospace !important; font-size: 1.7rem !important; }
[data-testid="stMetricDelta"]  { color: var(--green-2)      !important; }

/* ── Tabs ── */
[data-testid="stTabs"] [role="tab"] {
    color: var(--text-muted) !important;
    font-weight: 500;
    font-size: .9rem;
    padding: 10px 20px;
    border-radius: 8px 8px 0 0;
    transition: color .2s;
}
[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
    color: var(--green-1) !important;
    border-bottom: 2px solid var(--green-1) !important;
    background: rgba(0,255,136,0.05) !important;
}
[data-testid="stTabs"] [role="tablist"] {
    border-bottom: 1px solid var(--border) !important;
}

/* ── Sliders, selects, multiselects ── */
[data-baseweb="select"] > div,
[data-baseweb="input"]  > div  {
    background: var(--bg-card2) !important;
    border-color: var(--green-5) !important;
    color: var(--text-primary)  !important;
    border-radius: 8px !important;
}
[data-testid="stSlider"] [role="slider"] {
    background: var(--green-1) !important;
}
.stMultiSelect [data-baseweb="tag"] {
    background: var(--green-4) !important;
    color: var(--green-1) !important;
}

/* ── Headers ── */
h1 { font-family: 'Space Mono', monospace !important; color: var(--green-1) !important; letter-spacing: -.02em; }
h2, h3 { color: var(--text-primary) !important; font-weight: 600 !important; }

/* ── Divider ── */
hr { border-color: var(--border) !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar       { width: 6px; }
::-webkit-scrollbar-track { background: var(--bg-primary); }
::-webkit-scrollbar-thumb { background: var(--green-4); border-radius: 3px; }

/* ── Section label ── */
.section-label {
    font-family: 'Space Mono', monospace;
    font-size: .7rem;
    color: var(--green-2);
    letter-spacing: .15em;
    text-transform: uppercase;
    margin-bottom: 4px;
}

/* ── Plotly charts transparent bg ── */
.js-plotly-plot .plotly { background: transparent !important; }
</style>
""", unsafe_allow_html=True)

# ─── PLOTLY TEMPLATE ────────────────────────────────────────────────────────────
GREEN_SCALE   = ["#003d1f", "#006633", "#00994f", "#00cc6a", "#00ff88"]
GREEN_CONT    = [[0, "#003d1f"], [0.25, "#006633"], [0.5, "#00994f"],
                 [0.75, "#00cc6a"], [1.0, "#00ff88"]]

PLOT_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor ="rgba(0,0,0,0)",
    font         =dict(family="DM Sans", color="#e8f5e9", size=12),
    title_font   =dict(family="Space Mono", color="#00ff88", size=14),
    legend       =dict(bgcolor="rgba(0,0,0,0)", bordercolor="#1a2e1a", borderwidth=1),
    margin       =dict(l=10, r=10, t=40, b=10),
    xaxis        =dict(gridcolor="#1a2e1a", linecolor="#1a2e1a", tickfont=dict(color="#6b8f72")),
    yaxis        =dict(gridcolor="#1a2e1a", linecolor="#1a2e1a", tickfont=dict(color="#6b8f72")),
)

# ─── LOAD DATA ──────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    """Load CSV from same folder. Fallback to synthetic demo data."""
    try:
        df = pd.read_csv("cleaned_quick_commerce_data.csv")
    except FileNotFoundError:
        rng = np.random.default_rng(42)
        n   = 5000
        companies  = ["Swiggy Instamart","Flipkart Minutes","Dunzo","Jio Mart",
                       "Blinkit","Amazon Now","Big Basket","Zepto"]
        cities     = ["Noida","Amritsar","Delhi","Mumbai","Kolkata","Bengluru",
                      "Chennai","Hyderabad","Pune","Haridwar","Jaipur","Gurgaon"]
        categories = ["Dairy","Snacks","Household","Personal Care",
                      "Beverages","Groceries","Fruits & Vegetables"]
        payments   = ["Wallet","Cash on Delivery","Credit Card","UPI","Debit Card"]

        df = pd.DataFrame({
            "Order_ID"               : range(1_000_001, 1_000_001 + n),
            "Company"                : rng.choice(companies,  n),
            "City"                   : rng.choice(cities,     n),
            "Customer_Age"           : rng.integers(18, 60,   n),
            "Order_Value"            : rng.uniform(200, 2000, n).round(2),
            "Delivery_Time_Min"      : rng.uniform(5, 45,     n).round(3),
            "Distance_Km"            : rng.uniform(1, 15,     n).round(2),
            "Items_Count"            : rng.integers(1, 20,    n).astype(float),
            "Product_Category"       : rng.choice(categories, n),
            "Payment_Method"         : rng.choice(payments,   n),
            "Customer_Rating"        : rng.choice(np.arange(2.5, 5.1, 0.1).round(1), n),
            "Discount_Applied"       : rng.uniform(0, 50,     n).round(2),
            "Delivery_Partner_Rating": rng.choice(np.arange(2.5, 5.1, 0.1).round(1), n),
        })
    return df

df_raw = load_data()

# ─── SIDEBAR FILTERS ────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="section-label">⚡ Quick Commerce</div>', unsafe_allow_html=True)
    st.markdown("## Filters")
    st.markdown("---")

    # Company
    st.markdown('<div class="section-label">🏪 Company</div>', unsafe_allow_html=True)
    companies_all = sorted(df_raw["Company"].unique().tolist())
    sel_company   = st.multiselect("", companies_all, default=companies_all, key="company")

    # City
    st.markdown('<div class="section-label">🏙️ City</div>', unsafe_allow_html=True)
    cities_all = sorted(df_raw["City"].unique().tolist())
    sel_city   = st.multiselect("", cities_all, default=cities_all, key="city")

    # Category
    st.markdown('<div class="section-label">📦 Product Category</div>', unsafe_allow_html=True)
    cats_all = sorted(df_raw["Product_Category"].unique().tolist())
    sel_cat  = st.multiselect("", cats_all, default=cats_all, key="cat")

    # Payment
    st.markdown('<div class="section-label">💳 Payment Method</div>', unsafe_allow_html=True)
    pay_all = sorted(df_raw["Payment_Method"].unique().tolist())
    sel_pay = st.multiselect("", pay_all, default=pay_all, key="pay")

    st.markdown("---")

    # Order Value Range
    st.markdown('<div class="section-label">💰 Order Value (₹)</div>', unsafe_allow_html=True)
    val_min, val_max = float(df_raw["Order_Value"].min()), float(df_raw["Order_Value"].max())
    sel_val = st.slider("", val_min, val_max, (val_min, val_max), step=50.0, key="val")

    # Delivery Time
    st.markdown('<div class="section-label">⏱️ Delivery Time (min)</div>', unsafe_allow_html=True)
    dt_min, dt_max = float(df_raw["Delivery_Time_Min"].min()), float(df_raw["Delivery_Time_Min"].max())
    sel_dt = st.slider("", dt_min, dt_max, (dt_min, dt_max), step=1.0, key="dt")

    # Customer Age
    st.markdown('<div class="section-label">👤 Customer Age</div>', unsafe_allow_html=True)
    age_min, age_max = int(df_raw["Customer_Age"].min()), int(df_raw["Customer_Age"].max())
    sel_age = st.slider("", age_min, age_max, (age_min, age_max), key="age")

    # Rating
    st.markdown('<div class="section-label">⭐ Min Customer Rating</div>', unsafe_allow_html=True)
    sel_rating = st.slider("", 2.5, 5.0, 2.5, step=0.1, key="rating")

    # Delivery Partner Rating
    st.markdown('<div class="section-label">🚴 Min Delivery Partner Rating</div>', unsafe_allow_html=True)
    sel_dp_rating = st.slider("", 2.5, 5.0, 2.5, step=0.1, key="dp_rating")

    # Discount Applied
    st.markdown('<div class="section-label">🏷️ Discount Applied (%)</div>', unsafe_allow_html=True)
    disc_min = float(df_raw["Discount_Applied"].min())
    disc_max = float(df_raw["Discount_Applied"].max())
    sel_disc = st.slider("", disc_min, disc_max, (disc_min, disc_max), step=1.0, key="disc")

    st.markdown("---")
    st.markdown(f'<div class="section-label" style="text-align:center">Dashboard v1.0</div>',
                unsafe_allow_html=True)

# ─── APPLY FILTERS ──────────────────────────────────────────────────────────────
df = df_raw.copy()
if sel_company : df = df[df["Company"].isin(sel_company)]
if sel_city    : df = df[df["City"].isin(sel_city)]
if sel_cat     : df = df[df["Product_Category"].isin(sel_cat)]
if sel_pay     : df = df[df["Payment_Method"].isin(sel_pay)]
df = df[
    (df["Order_Value"].between(*sel_val)) &
    (df["Delivery_Time_Min"].between(*sel_dt)) &
    (df["Customer_Age"].between(*sel_age)) &
    (df["Customer_Rating"] >= sel_rating) &
    (df["Delivery_Partner_Rating"] >= sel_dp_rating) &
    (df["Discount_Applied"].between(*sel_disc))
]

# ─── HEADER ─────────────────────────────────────────────────────────────────────
st.markdown("# ⚡ Quick Commerce Analytics")
pct = len(df) / len(df_raw) * 100
st.markdown(
    f'<p style="color:#6b8f72;font-size:.9rem;margin-top:-10px">'
    f'Showing <span style="color:#00ff88;font-weight:600">{len(df):,}</span> orders '
    f'({pct:.1f}% of total) · Filtered from {len(df_raw):,} records</p>',
    unsafe_allow_html=True
)

# ─── KPI CARDS ──────────────────────────────────────────────────────────────────
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Total Orders",        f"{len(df):,}")
k2.metric("Total Revenue",       f"₹{df['Order_Value'].sum()/1e6:.2f}M")
k3.metric("Avg Order Value",     f"₹{df['Order_Value'].mean():,.0f}")
k4.metric("Avg Delivery (min)",  f"{df['Delivery_Time_Min'].mean():.1f}")
k5.metric("Avg Customer Rating", f"{df['Customer_Rating'].mean():.2f} ⭐")

st.markdown("<br>", unsafe_allow_html=True)

# ─── TABS ───────────────────────────────────────────────────────────────────────
tabs = st.tabs([
    "📊 Overview",
    "🏪 Companies",
    "🏙️ Cities",
    "📦 Products & Payments",
    "👤 Customers",
    "⏱️ Delivery Analysis",
])

# ════════════════════════════════════════════════════════════════════════════════
# TAB 1 – OVERVIEW
# ════════════════════════════════════════════════════════════════════════════════
with tabs[0]:
    c1, c2 = st.columns(2)

    # Revenue by company – horizontal bar
    with c1:
        rev = (df.groupby("Company")["Order_Value"]
                 .sum().sort_values().reset_index())
        fig = go.Figure(go.Bar(
            x=rev["Order_Value"], y=rev["Company"],
            orientation="h",
            marker=dict(color=rev["Order_Value"],
                        colorscale=GREEN_CONT, showscale=False),
            text=[f"₹{v/1e3:.0f}K" for v in rev["Order_Value"]],
            textposition="outside", textfont=dict(color="#e8f5e9", size=10),
        ))
        fig.update_layout(**PLOT_LAYOUT, title="Revenue by Company", height=320)
        fig.update_yaxes(gridcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

    # Orders by category – donut
    with c2:
        cat_cnt = df["Product_Category"].value_counts().reset_index()
        cat_cnt.columns = ["Category", "Count"]
        fig = go.Figure(go.Pie(
            labels=cat_cnt["Category"], values=cat_cnt["Count"],
            hole=.55,
            marker=dict(colors=GREEN_SCALE +
                        ["#00ff88","#00cc6a","#00994f"][:max(0, len(cat_cnt)-5)]),
            textfont=dict(color="#e8f5e9"),
        ))
        fig.update_layout(**PLOT_LAYOUT, title="Orders by Product Category", height=320)
        st.plotly_chart(fig, use_container_width=True)

    # Order Value distribution
    fig = go.Figure(go.Histogram(
        x=df["Order_Value"], nbinsx=60,
        marker=dict(color="#00cc6a", opacity=.85,
                    line=dict(color="#003d1f", width=.5)),
    ))
    fig.update_layout(**PLOT_LAYOUT,
                      title="Order Value Distribution (₹)",
                      xaxis_title="Order Value (₹)", yaxis_title="Frequency",
                      height=280)
    st.plotly_chart(fig, use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════════
# TAB 2 – COMPANIES
# ════════════════════════════════════════════════════════════════════════════════
with tabs[1]:
    c1, c2 = st.columns(2)

    with c1:
        # Avg customer rating per company
        rat = (df.groupby("Company")["Customer_Rating"]
                 .mean().sort_values(ascending=False).reset_index())
        fig = go.Figure(go.Bar(
            x=rat["Company"], y=rat["Customer_Rating"],
            marker=dict(color=rat["Customer_Rating"], colorscale=GREEN_CONT, showscale=False),
            text=rat["Customer_Rating"].round(2), textposition="outside",
            textfont=dict(color="#e8f5e9"),
        ))
        fig.update_layout(**PLOT_LAYOUT, title="Avg Customer Rating by Company",
                          yaxis_range=[0, 5.5], height=320)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        # Avg delivery partner rating per company
        dp = (df.groupby("Company")["Delivery_Partner_Rating"]
                .mean().sort_values(ascending=False).reset_index())
        fig = go.Figure(go.Bar(
            x=dp["Company"], y=dp["Delivery_Partner_Rating"],
            marker=dict(color=dp["Delivery_Partner_Rating"], colorscale=GREEN_CONT, showscale=False),
            text=dp["Delivery_Partner_Rating"].round(2), textposition="outside",
            textfont=dict(color="#e8f5e9"),
        ))
        fig.update_layout(**PLOT_LAYOUT, title="Avg Delivery Partner Rating by Company",
                          yaxis_range=[0, 5.5], height=320)
        st.plotly_chart(fig, use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        # Avg delivery time per company
        del_ = (df.groupby("Company")["Delivery_Time_Min"]
                  .mean().sort_values().reset_index())
        fig = go.Figure(go.Bar(
            x=del_["Company"], y=del_["Delivery_Time_Min"],
            marker=dict(color=del_["Delivery_Time_Min"],
                        colorscale=GREEN_CONT[::-1], showscale=False),
            text=del_["Delivery_Time_Min"].round(1),
            textposition="outside", textfont=dict(color="#e8f5e9"),
        ))
        fig.update_layout(**PLOT_LAYOUT, title="Avg Delivery Time (min) by Company",
                          height=320)
        st.plotly_chart(fig, use_container_width=True)
    with c4:
        # Avg discount per company
        disc_comp = (df.groupby("Company")["Discount_Applied"]
                       .mean().sort_values(ascending=False).reset_index())
        fig = go.Figure(go.Bar(
            x=disc_comp["Company"], y=disc_comp["Discount_Applied"],
            marker=dict(color=disc_comp["Discount_Applied"],
                        colorscale=GREEN_CONT, showscale=False),
            text=disc_comp["Discount_Applied"].round(1),
            textposition="outside", textfont=dict(color="#e8f5e9"),
        ))
        fig.update_layout(**PLOT_LAYOUT, title="Avg Discount Applied (%) by Company",
                          height=320)
        st.plotly_chart(fig, use_container_width=True)
    # Box plot order value per company
    fig = px.box(df, x="Company", y="Order_Value",
                 color_discrete_sequence=["#00cc6a"])
    fig.update_layout(**PLOT_LAYOUT, title="Order Value Distribution per Company",
                      height=320)
    st.plotly_chart(fig, use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════════
# TAB 3 – CITIES
# ════════════════════════════════════════════════════════════════════════════════
with tabs[2]:
    c1, c2 = st.columns(2)

    with c1:
        city_rev = (df.groupby("City")["Order_Value"]
                      .sum().sort_values(ascending=False).reset_index())
        fig = go.Figure(go.Bar(
            x=city_rev["City"], y=city_rev["Order_Value"],
            marker=dict(color=city_rev["Order_Value"],
                        colorscale=GREEN_CONT, showscale=False),
            text=[f"₹{v/1e3:.0f}K" for v in city_rev["Order_Value"]],
            textposition="outside", textfont=dict(color="#e8f5e9", size=10),
        ))
        fig.update_layout(**PLOT_LAYOUT, title="Revenue by City", height=320)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        city_orders = df["City"].value_counts().reset_index()
        city_orders.columns = ["City", "Orders"]
        fig = go.Figure(go.Bar(
            x=city_orders["City"], y=city_orders["Orders"],
            marker=dict(color=city_orders["Orders"],
                        colorscale=GREEN_CONT, showscale=False),
        ))
        fig.update_layout(**PLOT_LAYOUT, title="Order Count by City", height=320)
        st.plotly_chart(fig, use_container_width=True)

    # Heatmap: city × company order count
    heat = (df.groupby(["City","Company"])
              .size().reset_index(name="Count"))
    pivot = heat.pivot(index="City", columns="Company", values="Count").fillna(0)
    fig = go.Figure(go.Heatmap(
        z=pivot.values, x=pivot.columns.tolist(), y=pivot.index.tolist(),
        colorscale=GREEN_CONT, showscale=True,
        hoverongaps=False,
    ))
    fig.update_layout(**PLOT_LAYOUT, title="Orders Heatmap: City × Company", height=380)
    st.plotly_chart(fig, use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════════
# TAB 4 – PRODUCTS & PAYMENTS
# ════════════════════════════════════════════════════════════════════════════════
with tabs[3]:
    c1, c2 = st.columns(2)

    with c1:
        pay_cnt = df["Payment_Method"].value_counts().reset_index()
        pay_cnt.columns = ["Method", "Count"]
        fig = go.Figure(go.Pie(
            labels=pay_cnt["Method"], values=pay_cnt["Count"], hole=.5,
            marker=dict(colors=GREEN_SCALE),
            textfont=dict(color="#e8f5e9"),
        ))
        fig.update_layout(**PLOT_LAYOUT, title="Payment Method Share", height=320)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        cat_val = (df.groupby("Product_Category")["Order_Value"]
                     .mean().sort_values(ascending=False).reset_index())
        fig = go.Figure(go.Bar(
            x=cat_val["Product_Category"], y=cat_val["Order_Value"],
            marker=dict(color=cat_val["Order_Value"],
                        colorscale=GREEN_CONT, showscale=False),
            text=cat_val["Order_Value"].round(0),
            textposition="outside", textfont=dict(color="#e8f5e9"),
        ))
        fig.update_layout(**PLOT_LAYOUT, title="Avg Order Value by Category", height=320)
        st.plotly_chart(fig, use_container_width=True)

    # Items count distribution
    items = df["Items_Count"].value_counts().sort_index().reset_index()
    items.columns = ["Items", "Count"]
    fig = go.Figure(go.Bar(
        x=items["Items"].astype(int), y=items["Count"],
        marker=dict(color=items["Count"], colorscale=GREEN_CONT, showscale=False),
    ))
    fig.update_layout(**PLOT_LAYOUT, title="Items Count Frequency",
                      xaxis_title="Items in Order", yaxis_title="Count", height=280)
    st.plotly_chart(fig, use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════════
# TAB 5 – CUSTOMERS
# ════════════════════════════════════════════════════════════════════════════════
with tabs[4]:
    c1, c2 = st.columns(2)

    with c1:
        # Age distribution
        fig = go.Figure(go.Histogram(
            x=df["Customer_Age"], nbinsx=42,
            marker=dict(color="#00994f", opacity=.9,
                        line=dict(color="#003d1f", width=.4)),
        ))
        fig.update_layout(**PLOT_LAYOUT, title="Customer Age Distribution",
                          xaxis_title="Age", yaxis_title="Count", height=300)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        # Age group vs avg order value
        df["Age_Group"] = pd.cut(
            df["Customer_Age"],
            bins=[17, 25, 35, 45, 60],
            labels=["18-25", "26-35", "36-45", "46+"]
        )
        ag = (df.groupby("Age_Group", observed=True)["Order_Value"]
                .mean().reset_index())
        fig = go.Figure(go.Bar(
            x=ag["Age_Group"].astype(str), y=ag["Order_Value"],
            marker=dict(color=ag["Order_Value"],
                        colorscale=GREEN_CONT, showscale=False),
            text=ag["Order_Value"].round(0),
            textposition="outside", textfont=dict(color="#e8f5e9"),
        ))
        fig.update_layout(**PLOT_LAYOUT, title="Avg Order Value by Age Group",
                          height=300)
        st.plotly_chart(fig, use_container_width=True)

    # Scatter: age vs order value (sampled for performance)
    samp = df.sample(min(2000, len(df)), random_state=42)
    fig = px.scatter(
        samp, x="Customer_Age", y="Order_Value",
        color="Company",
        color_discrete_sequence=GREEN_SCALE + ["#00ff88","#006633","#003d1f"],
        opacity=.5, size_max=6,
    )
    fig.update_layout(**PLOT_LAYOUT,
                      title="Order Value vs Customer Age",
                      xaxis_title="Customer Age", yaxis_title="Order Value (₹)",
                      height=320)
    st.plotly_chart(fig, use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        # Customer Rating distribution
        rat_dist = df["Customer_Rating"].value_counts().sort_index().reset_index()
        rat_dist.columns = ["Rating", "Count"]
        fig = go.Figure(go.Bar(
            x=rat_dist["Rating"], y=rat_dist["Count"],
            marker=dict(color=rat_dist["Count"], colorscale=GREEN_CONT, showscale=False),
        ))
        fig.update_layout(**PLOT_LAYOUT, title="Customer Rating Distribution",
                          xaxis_title="Rating", height=300)
        st.plotly_chart(fig, use_container_width=True)

    with c4:
        # Discount vs Order Value scatter
        samp3 = df.sample(min(2000, len(df)), random_state=99)
        fig = px.scatter(
            samp3, x="Discount_Applied", y="Order_Value",
            color="Product_Category",
            color_discrete_sequence=GREEN_SCALE + ["#00ff88","#006633","#003d1f"],
            opacity=.5,
        )
        fig.update_layout(**PLOT_LAYOUT, title="Discount vs Order Value",
                          xaxis_title="Discount (%)", yaxis_title="Order Value (₹)",
                          height=300)
        st.plotly_chart(fig, use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════════
# TAB 6 – DELIVERY ANALYSIS
# ════════════════════════════════════════════════════════════════════════════════
with tabs[5]:
    c1, c2 = st.columns(2)

    with c1:
        # Delivery time distribution
        fig = go.Figure(go.Histogram(
            x=df["Delivery_Time_Min"], nbinsx=50,
            marker=dict(color="#00cc6a", opacity=.85,
                        line=dict(color="#003d1f", width=.4)),
        ))
        fig.update_layout(**PLOT_LAYOUT, title="Delivery Time Distribution",
                          xaxis_title="Minutes", height=300)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        # Avg delivery time per city
        city_dt = (df.groupby("City")["Delivery_Time_Min"]
                     .mean().sort_values().reset_index())
        fig = go.Figure(go.Bar(
            x=city_dt["City"], y=city_dt["Delivery_Time_Min"],
            marker=dict(color=city_dt["Delivery_Time_Min"],
                        colorscale=GREEN_CONT, showscale=False),
            text=city_dt["Delivery_Time_Min"].round(1),
            textposition="outside", textfont=dict(color="#e8f5e9"),
        ))
        fig.update_layout(**PLOT_LAYOUT,
                          title="Avg Delivery Time by City (min)", height=300)
        st.plotly_chart(fig, use_container_width=True)

    # Scatter: distance vs delivery time
    samp2 = df.sample(min(2000, len(df)), random_state=7)
    fig = px.scatter(
        samp2, x="Distance_Km", y="Delivery_Time_Min",
        color="Company",
        color_discrete_sequence=GREEN_SCALE + ["#00ff88","#006633","#003d1f"],
        trendline="ols", trendline_color_override="#00ff88",
        opacity=.4,
    )
    fig.update_layout(**PLOT_LAYOUT,
                      title="Distance vs Delivery Time",
                      xaxis_title="Distance (km)",
                      yaxis_title="Delivery Time (min)",
                      height=340)
    st.plotly_chart(fig, use_container_width=True)