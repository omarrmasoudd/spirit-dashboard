import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import os
from datetime import datetime


# ================= PAGE =================
st.set_page_config(
    page_title="Spirit Developments Dashboard",
    layout="wide"
)

# ================= SESSION =================
if "selected_project" not in st.session_state:
    st.session_state.selected_project = None

if "page" not in st.session_state:
    st.session_state.page = "📊 Portfolio Overview"


# ================= STYLE =================
st.markdown("""
<style>

html, body {
background-color:#0B1D1A;
color:white;
font-family:'Segoe UI', sans-serif;
}

.block-container{
padding-top:2rem;
}

.kpi-card{
background:linear-gradient(145deg,#102824,#081614);
padding:25px;
border-radius:16px;
border:1px solid rgba(212,175,55,0.25);
box-shadow:0px 6px 20px rgba(0,0,0,0.6);
text-align:center;
}

.kpi-title{
color:#BFA76A;
font-size:14px;
}

.kpi-value{
color:white;
font-size:34px;
font-weight:600;
}

section[data-testid="stSidebar"]{
background:#081614;
}

</style>
""", unsafe_allow_html=True)


# ================= DATA =================
file_path = "Spirit_Project_Template_CORRECT.xlsx"
xls = pd.ExcelFile(file_path)

summary = []

for sheet in xls.sheet_names:

    df = pd.read_excel(file_path, sheet_name=sheet, header=2)

    total = df["Unit Number"].notna().sum()

    sold = (
        df["Status"]
        .astype(str)
        .str.lower()
        .eq("sold")
        .sum()
    )

    sales = (sold / total * 100) if total else 0

    summary.append({
        "Project": sheet,
        "Total Units": total,
        "Sold Units": sold,
        "Sales %": round(sales,1)
    })

summary_df = pd.DataFrame(summary)


# ================= SIDEBAR =================
with st.sidebar:

    logo_path = os.path.join(os.getcwd(), "spirit_logo.png")

    if os.path.exists(logo_path):
        st.image(logo_path, width=120)

    st.markdown("### Spirit Dashboard")
    st.caption("Executive Control Panel")

    st.markdown("---")

    if st.button("📊 Portfolio Overview", use_container_width=True):
        st.session_state.page = "📊 Portfolio Overview"
        st.rerun()

    if st.button("🏗 Project Analysis", use_container_width=True):
        st.session_state.page = "🏗 Project Analysis"
        st.rerun()

    st.markdown("---")
    st.caption("Spirit Developments Internal System")

page = st.session_state.page


# ================= EXECUTIVE HEADER =================
st.markdown("""
<div style="
display:flex;
align-items:center;
gap:20px;
padding-bottom:25px;
border-bottom:1px solid rgba(212,175,55,0.2);
margin-bottom:25px;
">

<h1 style="color:#D4AF37;margin-bottom:0;">
Spirit Developments
</h1>

</div>
""", unsafe_allow_html=True)

st.caption(f"Last Updated: {datetime.now().strftime('%d %B %Y')}")


# =====================================================
# ================= PORTFOLIO PAGE ====================
# =====================================================
if page == "📊 Portfolio Overview":

    total_units = summary_df["Total Units"].sum()
    sold_units = summary_df["Sold Units"].sum()
    sellable_units = total_units - sold_units
    overall_sales = (sold_units / total_units) * 100

    # ================= KPI ROW =================
    st.markdown("## Portfolio Overview")

    k1,k2,k3,k4 = st.columns(4)

    def kpi_card(title,value):

        st.markdown(f"""
        <div class="kpi-card">
        <div class="kpi-title">{title}</div>
        <div class="kpi-value">{value}</div>
        </div>
        """, unsafe_allow_html=True)

    with k1:
        kpi_card("Total Units", total_units)

    with k2:
        kpi_card("Units Sold", sold_units)

    with k3:
        kpi_card("Portfolio Sales %",
                 f"{round(overall_sales,1)}%")

    with k4:
        kpi_card("Sellable Inventory",
                 sellable_units)


    # ================= PORTFOLIO HEALTH =================
    st.markdown("### Portfolio Health")

    gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=overall_sales,
        title={'text':"Sales Completion"},
        gauge={
            'axis':{'range':[0,100]},
            'bar':{'color':"#D4AF37"},
            'steps':[
                {'range':[0,40],'color':"#5c1a1a"},
                {'range':[40,70],'color':"#665c1a"},
                {'range':[70,100],'color':"#1a5c2e"},
            ]
        }
    ))

    st.plotly_chart(gauge,use_container_width=True)


    # ================= HEATMAP =================
    st.markdown("### Portfolio Sales Heatmap")

    heatmap_data = summary_df.set_index("Project")

    fig = go.Figure(
        data=go.Heatmap(
            z=heatmap_data["Sales %"].values.reshape(1,-1),
            x=heatmap_data.index,
            y=["Sales %"],
            colorscale="RdYlGn",
            zmin=0,
            zmax=100,
            text=[heatmap_data["Sales %"].round(1).astype(str) + "%"],
            texttemplate="%{text}",
            textfont={"color":"white","size":14},
            hovertemplate="<b>%{x}</b><br>Sales: %{z:.1f}%<extra></extra>"
        )
    )

    fig.update_layout(
        height=220,
        margin=dict(l=0,r=0,t=20,b=0),
        paper_bgcolor="#0B1D1A",
        plot_bgcolor="#0B1D1A",
        xaxis=dict(tickangle=-35),
        yaxis=dict(showticklabels=False)
    )

    st.plotly_chart(fig, use_container_width=True)


    # ================= PROJECT GRID =================
    st.markdown("## Projects")

    cols = st.columns(3)

    for i,row in summary_df.iterrows():

        with cols[i % 3]:

            sales = row["Sales %"]

            st.markdown(f"""
            <div style="
            background:#102824;
            border:1px solid rgba(212,175,55,0.2);
            border-radius:16px;
            padding:20px;
            margin-bottom:10px;
            ">

            <h3 style="color:#D4AF37;">
            {row['Project']}
            </h3>

            <p style="color:white;font-size:20px;">
            {sales}% Sold
            </p>

            </div>
            """, unsafe_allow_html=True)

            st.caption(
                f"{row['Sold Units']} / {row['Total Units']} Units Sold"
            )

            if st.button("Open Project",key=row["Project"]):

                st.session_state.selected_project = row["Project"]
                st.session_state.page = "🏗 Project Analysis"
                st.rerun()


# =====================================================
# ================= PROJECT PAGE ======================
# =====================================================
if page == "🏗 Project Analysis":

    selected_project = st.selectbox(
        "Select Project",
        xls.sheet_names,
        index=(xls.sheet_names.index(st.session_state.selected_project)
        if st.session_state.selected_project in xls.sheet_names else 0)
    )

    df = pd.read_excel(
        file_path,
        sheet_name=selected_project,
        header=2
    )

    total = df["Unit Number"].notna().sum()

    sold = (
        df["Status"]
        .astype(str)
        .str.lower()
        .eq("sold")
        .sum()
    )

    sales = (sold/total*100) if total else 0

    c1,c2,c3 = st.columns(3)

    c1.metric("Total Units", total)
    c2.metric("Sold Units", sold)
    c3.metric("Sales %", round(sales,1))


    # ===== BROCHURE =====
    st.markdown("### 📄 Project Brochure")

    brochure_path = f"brochures/{selected_project}.pdf"

    if os.path.exists(brochure_path):

        with open(brochure_path,"rb") as pdf:

            st.download_button(
                "Open Project Brochure",
                pdf,
                file_name=f"{selected_project}.pdf",
                use_container_width=True
            )

    else:
        st.info("No brochure available.")


    # ===== SALES GAUGE =====
    gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=sales,
        title={'text':"Sales Completion"},
        gauge={'axis':{'range':[0,100]},
               'bar':{'color':"#D4AF37"}}
    ))

    st.plotly_chart(gauge,use_container_width=True)


    # ===== INVENTORY TABLE =====
    st.markdown("### Unit Inventory")

    def color_status(row):

        status = str(row["Status"]).lower()

        if status == "sold":
            return ["background-color:#1f4e2c;color:white"]*len(row)

        elif status == "closed":
            return ["background-color:#5c3b00;color:white"]*len(row)

        return ["background-color:#111111;color:white"]*len(row)

    styled_df = df.style.apply(color_status, axis=1)

    st.dataframe(
        styled_df,
        use_container_width=True,
        height=500
    )


    # ===== INVENTORY DISTRIBUTION =====
    st.markdown("### Inventory Distribution")

    status_clean = (
        df["Status"]
        .astype(str)
        .str.strip()
        .replace({
            "closed":"Management Hold"
        })
        .str.title()
        .value_counts()
    )

    st.bar_chart(status_clean)