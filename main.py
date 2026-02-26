import streamlit as st
from data.apps import projects

st.set_page_config(page_title="AI Store", layout="wide")

apps_ = [p for p in projects if p['page'][0]=='Streamlit']
VERSION = 'v1.3.0'

# 將 pages 用 dict 分組
pages = {
    "🏠 Home": [
        st.Page("views/home.py", default=True),
    ],
    "🧰 Application": [
        st.Page(f"views/apps/{a['page'][1]}.py", title=f"{a['application_type']}") for a in apps_
    ],
    "📊 Dashboard": [
        st.Page("views/dashboard.py", title="Projects Dashboard"),
    ]
}

nav = st.navigation(pages, position="sidebar", expanded=True)
nav.run()

st.sidebar.markdown(
    f"""
    <div style="position: fixed; bottom: 20px; width: 260px; font-size: 12px; color: gray; text-align: center;">
        Platform Version<br>
        <b>{VERSION}</b>
    </div>
    """,
    unsafe_allow_html=True
)
