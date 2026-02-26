import streamlit as st
import pandas as pd
# import matplotlib.pyplot as plt

# plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei'] # 修改中文字體
# plt.rcParams['axes.unicode_minus'] = False # 顯示負號
import plotly.express as px
from data.apps import projects


# ----------------------------------
# 資料前處理
# ----------------------------------
projects_ = sorted(projects, key=lambda x: (x['uid']))
# projects_ = projects_[:-1]
df_dashboard = pd.DataFrame(projects_)
df_dashboard = df_dashboard[['project_name', 'application_type', 'data_type', 'dev_team', 'is_lead', 'confluence']]
df_dashboard.columns = ['Project Name', 'Application Type', 'Data Type', 'Dev Teams', 'is Lead', 'Confluence']
df_dashboard['Score'] = df_dashboard.apply(lambda x: 1 if x['is Lead'] else 1, axis=1)


# Dev Team 展開（多對多）
dev_team_flat = []
for _, p in df_dashboard.iterrows():
    s = p["Score"]
    for team in p["Dev Teams"]:
        dev_team_flat.append({"project_name": p["Project Name"], "dev_teams": team, "score": s})

df_team = pd.DataFrame(dev_team_flat)

# ----------------------------------
# UI Layout
# ----------------------------------

st.set_page_config(page_title="Project Dashboard", layout="wide")
st.title("📊 Project Dashboard")


with st.container():
    col1, col2, col3 = st.columns(3)

    # ---------
    # 左：冠軍隊伍
    # ---------
    with col1:
        if not df_team.empty:
            grouped = df_team.groupby(['dev_teams']).agg(
                score_sum=('score', 'sum')
            ).reset_index().sort_values(by='score_sum', ascending=False)

            # champion_team, second_team = df_team["dev_team"].value_counts().index[:2]
            champion_team, second_team = grouped['dev_teams'][:2].values
            st.metric("Champion Team", champion_team, second_team, border=True, height=130)

    # ---------
    # 中：Application Count
    # ---------
    with col2:
        if not df_dashboard.empty:
            lead_project = df_dashboard.loc[df_dashboard['is Lead'] == True, :]
            st.metric("Application Count", f"{len(lead_project)}", border=True, height=130)

    # ---------
    # 右：Project Count
    # ---------
    with col3:
        st.metric("Project Count", str(len(df_dashboard)),  border=True, height=130)


if not df_dashboard.empty:
    ## show dataframe
    # st.dataframe(df_dashboard, height=300)
    st.data_editor(
        df_dashboard,
        height=300,
        column_config={
            "Confluence": st.column_config.LinkColumn(
                "報告連結",
                # display_text="🔗 View"
            ),
            "is Lead": st.column_config.CheckboxColumn(
                "領導專案",
                disabled=True,
            ),
            "Data Type": st.column_config.MultiselectColumn(
                "Data Type",
                help="The data type of the project",
                options=[
                    "tabular data",
                    "image",
                    "time series",
                    "cross modality",
                ],
                color=["#118cdf", "#d26363", "#23cfd4", "#84155c"],
                disabled=True,
            ),
        },
        # disabled=True,
    )

    ## show score bar chart
    df_team_sum = (
        df_team.groupby("dev_teams", as_index=False)
            .agg(total_score=("score", "sum"))
            .sort_values("total_score", ascending=False)
    )
    fig = px.bar(
        df_team_sum[["dev_teams", "total_score"]],
        x="dev_teams",
        y="total_score",
        title=f"得分統計",
        color_discrete_sequence=["#ffa940"]
    )
    fig.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    st.plotly_chart(fig, use_container_width=True)



with st.container():
    col1, col2 = st.columns(2)

    # ---------
    # 左：Application Type 分佈
    # ---------
    with col1:
        if not df_dashboard.empty:
            app_counts = df_dashboard["Application Type"].value_counts().reset_index()
            app_counts.columns = ["application_type", "count"]
            fig_app = px.pie(app_counts, names="application_type", values="count", title="應用類型分佈", hole=0.3)
            fig_app.update_layout(width=400, height=400, margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig_app, use_container_width=True)

    # ---------
    # 中：Dev Team 分佈
    # ---------
    with col2:
        if not df_team.empty:
            team_counts = df_team["dev_teams"].value_counts().reset_index()
            team_counts.columns = ["dev_teams", "count"]
            fig_team = px.pie(team_counts, names="dev_teams", values="count", title="開發團隊分佈", hole=0.3)
            fig_team.update_layout(width=400, height=400, margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig_team, use_container_width=True)
        else:
            st.info("沒有可用的開發團隊資料")