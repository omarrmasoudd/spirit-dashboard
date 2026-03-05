import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import os
from datetime import datetime


# ================= SESSION =================
if "selected_project" not in st.session_state:
    st.session_state.selected_project = None

if "page" not in st.session_state:
    st.session_state.page = "📊 Portfolio Overview"


# ================= STYLE =================
st.markdown("""
<style>

html, body, [class*="css"] {
    font-family:'Segoe UI',sans-serif;
    background-color:#0B1D1A;
}

h1,h2,h3 {
    color:#D4AF37;
}

.card{
    background:#102824;
    padding:22px;
    border-radius:16px;
    border:1px solid rgba(212,175,55,0.25);
}

section[data-testid="stSidebar"]{
    background:#081614;
}

.stProgress > div > div > div > div {
    background-color:#D4AF37;
}

.block-container{
    padding-top:1rem;
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

    st.image("spirit_logo.png", width=120)

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

<img src="spirit_logo.png" width="70">

<div>

<h1 style="color:#D4AF37;margin-bottom:0;">
Spirit Developments
</h1>

<p style="
color:#BFA76A;
font-size:18px;
margin-top:0;">
Executive Portfolio Dashboard
</p>

</div>

</div>
""", unsafe_allow_html=True)

st.caption(f"Last Updated: {datetime.now().strftime('%d %B %Y')}")


# =====================================================
# ================= KPI CARD FUNCTION =================
# =====================================================
def kpi_card(title,value):

    st.markdown(f"""
    <div style="
    background:linear-gradient(145deg,#102824,#081614);
    border:1px solid rgba(212,175,55,0.25);
    padding:25px;
    border-radius:16px;
    text-align:center;
    box-shadow:0px 6px 20px rgba(0,0,0,0.6);
    ">

    <p style="
    color:#BFA76A;
    font-size:14px;
    margin-bottom:5px;">
    {title}
    </p>

    <h2 style="
    color:white;
    margin-top:0;
    font-size:34px;">
    {value}
    </h2>

    </div>
    """, unsafe_allow_html=True)


# =====================================================
# ================= PORTFOLIO PAGE ====================
# =====================================================
if page == "📊 Portfolio Overview":

    total_units = summary_df["Total Units"].sum()
    sold_units = summary_df["Sold Units"].sum()
    sellable_units = total_units - sold_units
    overall_sales = (sold_units / total_units) * 100


    # ===== PORTFOLIO FINANCIALS =====
    company_total_value = 0
    company_sold_value = 0
    project_revenue = []

    for sheet in xls.sheet_names:

        temp_df = pd.read_excel(file_path, sheet_name=sheet, header=2)

        temp_df["Total Unit Price"] = pd.to_numeric(
            temp_df["Total Unit Price"], errors="coerce"
        )

        total_value = temp_df["Total Unit Price"].sum()

        sold_value = temp_df[
            temp_df["Status"].astype(str).str.lower()=="sold"
        ]["Total Unit Price"].sum()

        company_total_value += total_value
        company_sold_value += sold_value

        project_revenue.append({
            "Project": sheet,
            "Revenue": sold_value
        })

    company_remaining_value = company_total_value - company_sold_value

    revenue_df = pd.DataFrame(project_revenue)


    # ================= KPI ROW =================
    st.markdown("## Portfolio Overview")

    k1,k2,k3,k4 = st.columns(4)

    with k1:
        kpi_card("Total Units", total_units)

    with k2:
        kpi_card("Units Sold", sold_units)

    with k3:
        kpi_card("Portfolio Sales %",
                 f"{round(overall_sales,1)}%")

    with k4:
        kpi_card("Sellable Inventory", sellable_units)


    # ================= REVENUE ROW =================
    st.markdown("### Portfolio Revenue")

    r1,r2,r3 = st.columns(3)

    r1.metric("Portfolio Value",
              f"{company_total_value:,.0f} EGP")

    r2.metric("Sold Value",
              f"{company_sold_value:,.0f} EGP")

    r3.metric("Remaining Value",
              f"{company_remaining_value:,.0f} EGP")


    st.markdown("---")


    # ================= TWO COLUMN ANALYTICS =================
    col1,col2 = st.columns(2)


    with col1:

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


    with col2:

        st.markdown("### Project Revenue Ranking")

        revenue_df = revenue_df.sort_values(
            by="Revenue", ascending=False
        )

        st.bar_chart(
            revenue_df.set_index("Project")["Revenue"]
        )


    st.markdown("---")


    # ================= SALES TABLE =================
    st.markdown("### Portfolio Sales Heatmap")

    heatmap_data = summary_df.pivot_table(
        values="Sales %",
        index="Project"
    )

    st.dataframe(heatmap_data,use_container_width=True)


    # ================= STRATEGIC INSIGHTS =================
    st.markdown("### Strategic Insights")

    best_project = summary_df.loc[
        summary_df["Sales %"].idxmax()
    ]

    worst_project = summary_df.loc[
        summary_df["Sales %"].idxmin()
    ]

    i1,i2 = st.columns(2)

    i1.success(
        f"Best Project: {best_project['Project']} "
        f"({best_project['Sales %']}%)"
    )

    i2.warning(
        f"Needs Attention: {worst_project['Project']} "
        f"({worst_project['Sales %']}%)"
    )


    st.markdown("---")


    # ================= PROJECT GRID =================
    st.markdown("## Projects")

    cols = st.columns(3)

    for i,row in summary_df.iterrows():

        with cols[i % 3]:

            sales = row["Sales %"]

            if sales >= 70:
                color = "#1a5c2e"
            elif sales >= 40:
                color = "#665c1a"
            else:
                color = "#5c1a1a"

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

            st.progress(sales/100)

            if st.button("Open Project",key=row["Project"]):

                st.session_state.selected_project=row["Project"]
                st.session_state.page="🏗 Project Analysis"
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

    df = pd.read_excel(file_path,sheet_name=selected_project,header=2)

    total = df["Unit Number"].notna().sum()

    sold = (
        df["Status"].astype(str).str.lower().eq("sold").sum()
    )

    sales = (sold/total*100) if total else 0

    c1,c2,c3 = st.columns(3)

    c1.metric("Total Units",total)
    c2.metric("Sold Units",sold)
    c3.metric("Sales %",round(sales,1))


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

    styled_df = df.style.apply(color_status,axis=1)

    st.dataframe(styled_df,use_container_width=True,height=500)


    # ===== INVENTORY DISTRIBUTION =====
    st.markdown("### Inventory Distribution")

    status_clean = (
        df["Status"]
        .astype(str)
        .str.strip()
        .replace({"closed":"Management Hold"})
        .str.title()
        .value_counts()
    )

    st.bar_chart(status_clean)