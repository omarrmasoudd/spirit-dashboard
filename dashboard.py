import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import os
from datetime import datetime

# ================= LOGIN SYSTEM =================

users_file = "users.xlsx"
users_df = pd.read_excel(users_file, engine="openpyxl")

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "role" not in st.session_state:
    st.session_state.role = None


def login_screen():

    st.markdown("""
    <style>

    .login-box{
        max-width:420px;
        margin:auto;
        margin-top:120px;
        padding:40px;
        border-radius:16px;
        background:linear-gradient(145deg,#102824,#081614);
        border:1px solid rgba(212,175,55,0.25);
        box-shadow:0px 6px 25px rgba(0,0,0,0.6);
        text-align:center;
    }

    .login-title{
        color:#D4AF37;
        font-size:32px;
        margin-bottom:10px;
    }

    .login-sub{
        color:#BFA76A;
        margin-bottom:25px;
    }

    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="login-box">
        <div class="login-title">Spirit Developments</div>
        <div class="login-sub">Internal Dashboard Access</div>
    </div>
    """, unsafe_allow_html=True)

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login", use_container_width=True):

        user = users_df[
            (users_df["username"] == username) &
            (users_df["password"] == password)
        ]

        if not user.empty:

            role = user.iloc[0]["role"]

            st.session_state.authenticated = True
            st.session_state.role = role

            st.rerun()

        else:
            st.error("Invalid username or password")


if not st.session_state.authenticated:
    login_screen()
    st.stop()
    
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
    
    if st.button("📊 CRM Intelligence", use_container_width=True):
        st.session_state.page = "📊 CRM Intelligence"
        st.rerun()

    st.markdown("---")

    st.caption("Spirit Developments Internal System")

    st.markdown("---")
    if st.session_state.role == "manager":
        if st.button("👤 User Management", use_container_width=True):
            st.session_state.page = "👤 User Management"
            st.rerun()

    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.role = None
        st.rerun()

# IMPORTANT LINE
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

    if st.session_state.role != "manager":
        st.warning("Managers only section")
        st.stop()

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
    
# =====================================================
# ================= USER MANAGEMENT ===================
# =====================================================

if page == "👤 User Management":

    if st.session_state.role != "manager":
        st.error("Managers only")
        st.stop()

    st.title("User Management")

    users_file = "users.xlsx"
    users_df = pd.read_excel(users_file)

    st.markdown("### Existing Users")
    st.dataframe(users_df, use_container_width=True)

    st.markdown("---")

    # ================= CREATE USER =================

    st.markdown("### Create User")

    new_user = st.text_input("Username")
    new_pass = st.text_input("Password", type="password")
    new_role = st.selectbox("Role", ["viewer","manager"])

    if st.button("Create User"):

        if new_user in users_df["username"].values:
            st.error("User already exists")

        else:

            new_row = pd.DataFrame({
                "username":[new_user],
                "password":[new_pass],
                "role":[new_role]
            })

            users_df = pd.concat([users_df,new_row],ignore_index=True)

            users_df.to_excel(users_file,index=False)

            st.success("User created")
            st.rerun()

    st.markdown("---")

    # ================= DELETE USER =================

    st.markdown("### Delete User")

    delete_user = st.selectbox(
        "Select user",
        users_df["username"]
    )

    if st.button("Delete User"):

        users_df = users_df[
            users_df["username"] != delete_user
        ]

        users_df.to_excel(users_file,index=False)

        st.success("User deleted")
        st.rerun()

    st.markdown("---")

    # ================= CHANGE PASSWORD =================

    st.markdown("### Change Password")

    user_change = st.selectbox(
        "Select user to update",
        users_df["username"],
        key="changeuser"
    )

    new_password = st.text_input(
        "New password",
        type="password"
    )

    if st.button("Update Password"):

        users_df.loc[
            users_df["username"] == user_change,
            "password"
        ] = new_password

        users_df.to_excel(users_file,index=False)

        st.success("Password updated")
        st.rerun()

# =====================================================
# ================= CRM INTELLIGENCE ==================
# =====================================================

if page == "📊 CRM Intelligence":

    st.markdown("## CRM Intelligence Report")

    uploaded_file = st.file_uploader(
        "Upload CRM Export (Excel)",
        type=["xlsx"]
    )

    if uploaded_file:

        crm_df = pd.read_excel(uploaded_file)

        st.success("CRM File Loaded Successfully")

        # ================= ARABIC COMMENT ANALYSIS =================

        st.markdown("---")
        st.markdown("### 🧠 Lost Lead Analysis (Arabic Comments)")

        comment_column = "Last Comment"

        keywords = {
            "💰 Price Issue": ["سعر","غالي","الميزانية"],
            "🏢 Competitor Project": ["مشروع تاني","شركة تانية","منافس"],
            "🤷 Not Serious": ["مش مهتم","مش جاد","راجع بعدين"],
            "📐 Size Issue": ["مساحة","اصغر","اكبر"],
            "📍 Location Issue": ["الموقع"],
            "⏳ Postponed Decision": ["هياجل","بعد رمضان","بعد العيد"]
        }

        reason_counts = {
            key:0 for key in keywords
        }

        for comment in crm_df[comment_column].dropna():

            for reason,words in keywords.items():

                if any(word in str(comment) for word in words):

                    reason_counts[reason] += 1

        reason_df = pd.DataFrame(
            reason_counts.items(),
            columns=["Reason","Count"]
        )

        st.bar_chart(
            reason_df.set_index("Reason")
        )

        # ================= CLEAN DATA =================
        crm_df["Creation Date"] = pd.to_datetime(
            crm_df["Creation Date"], errors="coerce"
        )

        crm_df["Last Action Date"] = pd.to_datetime(
            crm_df["Last Action Date"], errors="coerce"
        )

        # ================= TOTAL LEADS =================
        total_leads = len(crm_df)

        # ================= BROKER PERFORMANCE =================
        broker_stats = (
            crm_df.groupby("Sales Rep")
            .size()
            .reset_index(name="Leads")
        )

        # ================= FOLLOW UP ACTIVITY =================
        followups = (
            crm_df.groupby("Sales Rep")["Last Action Date"]
            .count()
            .reset_index(name="Followups")
        )

        broker_stats = broker_stats.merge(
            followups,
            on="Sales Rep",
            how="left"
        )

        broker_stats["Activity Score"] = (
            broker_stats["Followups"] /
            broker_stats["Leads"]
        ).round(2)

        broker_stats = broker_stats.sort_values(
            "Leads",
            ascending=False
        )

        # ================= PROJECT INTEREST =================
        project_interest = (
            crm_df["Project"]
            .value_counts()
            .reset_index()
        )

        project_interest.columns = ["Project","Leads"]

        # ================= LEAD SOURCE =================
        lead_source = (
            crm_df["Channel"]
            .value_counts()
            .reset_index()
        )

        lead_source.columns = ["Channel","Leads"]

        # ================= LOST REASONS =================
        lost_reasons = (
            crm_df["Cancel Reason"]
            .dropna()
            .value_counts()
            .reset_index()
        )

        lost_reasons.columns = ["Reason","Count"]

        # ================= KPI =================
        c1,c2,c3 = st.columns(3)

        with c1:
            st.metric("Total Leads", total_leads)

        with c2:
            st.metric(
                "Active Brokers",
                crm_df["Sales Rep"].nunique()
            )

        with c3:
            st.metric(
                "Projects Requested",
                crm_df["Project"].nunique()
            )

        st.markdown("---")

        # ================= SALES FUNNEL =================

        st.markdown("---")
        st.markdown("### 🧭 Sales Funnel (Lead Conversion)")

        # Detect possible status column
        possible_status_cols = [
            "Status",
            "Lead Status",
            "Stage",
            "Pipeline Status"
        ]

        status_col = None
        for col in possible_status_cols:
            if col in crm_df.columns:
                status_col = col
                break

        if status_col is not None:

            crm_df["Status Clean"] = (
                crm_df[status_col]
                .astype(str)
                .str.strip()
                .str.lower()
            )

            def map_stage(status):
                if "new" in status:
                    return "New Lead"
                elif "contact" in status:
                    return "Contacted"
                elif "view" in status:
                    return "Viewing"
                elif "negotiat" in status:
                    return "Negotiation"
                elif "sold" in status or "closed" in status:
                    return "Closed"
                elif "cancel" in status or "lost" in status:
                    return "Lost"
                return "Other"

            crm_df["Funnel Stage"] = crm_df["Status Clean"].apply(map_stage)

            funnel_counts = (
                crm_df["Funnel Stage"]
                .value_counts()
                .reindex([
                    "New Lead",
                    "Contacted",
                    "Viewing",
                    "Negotiation",
                    "Closed",
                    "Lost"
                ])
                .fillna(0)
            )

            fig = go.Figure(go.Funnel(
                y=funnel_counts.index,
                x=funnel_counts.values,
                textinfo="value+percent initial",
                marker=dict(color="#D4AF37")
            ))

            fig.update_layout(
                plot_bgcolor="#0B1D1A",
                paper_bgcolor="#0B1D1A",
                font=dict(color="white"),
                height=500
            )

            st.plotly_chart(fig, use_container_width=True)

        else:
            st.warning("⚠️ No status column found in CRM file")

        # ================= BROKER LEADERBOARD =================
        st.markdown("### 🏆 Broker Performance")

        st.dataframe(
            broker_stats,
            use_container_width=True
        )

        # ================= PROJECT DEMAND =================
        import plotly.express as px

        st.markdown("### 📊 Project Demand")

        project_interest = project_interest.sort_values(
             "Leads",
             ascending=True
        )

        fig = px.bar(
            project_interest,
            x="Leads",
            y="Project",
            orientation="h",
            text="Leads",
            color="Leads",
            color_continuous_scale="ylgn"
        )

        fig.update_layout(
            height=400,
            plot_bgcolor="#0B1D1A",
            paper_bgcolor="#0B1D1A",
            font=dict(color="white"),
            coloraxis_showscale=False
        )

        fig.update_traces(
            textposition="outside"
        )

        st.plotly_chart(fig, use_container_width=True)

        # ================= LEAD SOURCE =================
        st.markdown("### 📈 Lead Source Performance")

        st.bar_chart(
            lead_source.set_index("Channel")
        )

        # ================= LOST LEADS =================
        st.markdown("### ❌ Lost Lead Reasons")

        st.bar_chart(
            lost_reasons.set_index("Reason")
        )

        # ================= RAW CRM TABLE =================
        st.markdown("### CRM Data")

        st.dataframe(
            crm_df,
            use_container_width=True
        )

        # ================= LEAD AGING =================

        st.markdown("---")
        st.markdown("### 🚨 Lead Aging Detection")

        crm_df["Days Since Action"] = (
            pd.Timestamp.now() - crm_df["Last Action Date"]
        ).dt.days

        critical_leads = crm_df[crm_df["Days Since Action"] >= 7]

        aging_leads = crm_df[
            (crm_df["Days Since Action"] >= 3) &
            (crm_df["Days Since Action"] < 7)
        ]

        healthy_leads = crm_df[crm_df["Days Since Action"] < 3]

        c1,c2,c3 = st.columns(3)

        with c1:
            st.metric(
                "🔴 Critical Leads",
                len(critical_leads)
            )

        with c2:
            st.metric(
                "🟠 Aging Leads",
                len(aging_leads)
            )

        with c3:
            st.metric(
                "🟢 Healthy Leads",
                len(healthy_leads)
            )

        st.markdown("#### Critical Leads (No Follow-Up)")

        st.dataframe(
            critical_leads[
                [
                    "Full Name",
                    "Sales Rep",
                    "Project",
                    "Last Action Date",
                    "Days Since Action"
                ]
            ],
            use_container_width=True
        )