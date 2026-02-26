import streamlit as st
from data import apps


# 自訂 CSS
st.markdown(
    """
    <style>
    .card {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 16px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);

        /* 讓卡片內容垂直分布：上=標題，中=描述，下=按鈕 */
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        height: 240px; /* 卡片固定高度 */
    }
    .card-title {
        font-size: 18px;
        font-weight: 600;
        margin-bottom: 8px;
    }
    .card-tags {
        display: flex;
        flex-wrap: wrap;
        margin-bottom: 4px;
    }
    .card-tag {
        background: #f0f5ff;   /* 淡藍底 */
        color: #1677ff;        /* 主色 */
        font-size: 12px;
        padding: 4px 10px;
        border-radius: 16px;   /* 膠囊形狀 */
        font-weight: 500;
        border: 1px solid #d6e4ff; /* 細邊框 */
        white-space: nowrap;   /* 避免標籤內斷行 */
        margin-left: 4px;
    }
    .card-dev-tag {
        background: #f6ffed;   /* 淡綠底 */
        color: #52c41a;        /* 主色：綠色 */
        font-size: 12px;
        padding: 4px 10px;
        border-radius: 16px;
        font-weight: 500;
        border: 1px solid #d9f7be;
        white-space: nowrap;
        margin-left: 4px;
    }
    .card-desc {
        font-size: 14px;
        color: #666;
        flex-grow: 1; /* 撐開中間空間 */
        margin-bottom: 12px;

        display: -webkit-box;
        -webkit-line-clamp: 4; /* 可改行數 */
        -webkit-box-orient: vertical;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    /* hover 顯示 tooltip */
    .card-desc:hover::after {
        content: attr(data-full);
        position: absolute;
        left: 0;
        top: 100%;
        z-index: 999;

        min-width: 260px;
        max-width: 360px;
        background: #333;
        color: white;
        padding: 8px 12px;
        border-radius: 8px;
        font-size: 14px;
        line-height: 1.4;

        white-space: normal;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);

        opacity: 0;
        animation: fadeIn .15s forwards;
    }

    /* fadeIn 動畫 */
    @keyframes fadeIn {
        to { opacity: 1; }
    }

    .card-btn {
        text-align: left; /* 按鈕靠右 */
        margin-top: 4px;
        margin-bottom: 12px;
    }
    .page-btn {
        background:#1677ff;
        border:none;
        color:white;
        padding:8px 16px;
        border-radius:8px;
        cursor:pointer;
        font-size: 14px;
        margin-bottom: 12px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# 定義 AI Apps
apps_ = apps.projects
apps_ = [app for app in apps_ if app['is_lead']]
## 依字母排序與uid排序
apps_ = sorted(apps_, key=lambda x: (x['uid']))

# 畫面主體
with st.container():
    st.title("🚀 AI Store")

    # 用 4 column 排卡片
    cols = st.columns(4)

    for i, app in enumerate(apps_):
        with cols[i % 4]:
            # 先建立卡片框架
            full_desc = app['desc'].replace('"', '&quot;')

            st.markdown(f"""
                <div class="card">
                    <div class="card-title">{app['application_type']}</div>
                    <div class="card-desc" data-full="{full_desc}">{app['desc']}</div>
                    <div class="card-tags">{"".join([f'<span class="card-dev-tag">{team}</span>' for team in app['dev_team']])}</div>
                    <div class="card-tags">{"".join([f'<span class="card-tag">{tag}</span>' for tag in app['data_type']])} <span class="card-tag">{app['project_name']}</span></div>
            """, unsafe_allow_html=True)

            # 🔹 URL 類型
            if app['page'][0] == "URL":
                st.markdown(
                    f"""
                    <div class="card-btn">
                        <a href="{app['page'][1]}" target="_blank">
                            <button class="page-btn">Open in Swagger UI</button>
                        </a>
                    </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            # 🔹 Streamlit 類型
            elif app['page'][0] == "Streamlit":
                with st.container():
                    # btn_col = st.columns([0.6, 0.4])  # 控制按鈕位置靠右
                    # with btn_col[1]:
                    if st.button(f"Go to app", key=f"button_{i}"):
                        #st.session_state["current_page"] = app['page'][1]
                        st.switch_page(f"views/apps/{app['page'][1]}.py")

                # 補上關閉 div
                st.markdown("</div>", unsafe_allow_html=True)