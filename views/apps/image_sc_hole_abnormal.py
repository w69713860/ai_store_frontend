import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import requests, json

from utils.utils import error_trace_back

from wecpy.config_manager import ConfigManager
ConfigManager('config.yaml')
from wecpy.log_manager import LogManager
logger = LogManager.get_logger()

import base64, io
from PIL import Image
from data.apps import projects

# TODO 加入檔案限制 (20 Mb)

sc_hole_abnormal_app = projects[1]

st.title("📷 Image Recognition")

# 建立 2:1 欄位
col_text, col_img = st.columns([2, 1])

with col_text:
    st.markdown("""
    ### SC Hole Abnormal Classificationn
    利用影像處理手法自動分析SC Hole Top View 影像，辨識是否存在偏移(Shift)與縮孔(Shrinkage)。
                
    **影像條件**
    - FOV: 1500 nm
    """)

with col_img:
    img_col, _ = st.columns([2, 1])  # 👈 中間縮
    
    with img_col:      
        image = Image.open("assets/image_sc_hole_abnormal/EK34102300_FW0BD004SE_20240328202434_46112_1_0.jpg")  # 換成你的圖片路徑
        st.image(image, use_container_width=True, width=160)



if 'files_data' not in st.session_state:
    st.session_state.files_data = []

if 'files_results' not in st.session_state:
    st.session_state.files_results = None


tab1, tab2 = st.tabs(
    ["選擇影像", "辨識結果"], default="選擇影像"
)

with tab1:
    with st.form("input_form"):

        uploaded_files = st.file_uploader("請上傳影像檔（最多 10 個）", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
        if uploaded_files is not None:
            if len(uploaded_files) > 10:
                    st.error("❌ 最多只能上傳 10 個影像檔")
            else:
                # st.success(f"✅ 已上傳 {len(uploaded_files)} 個檔案")
                for file in uploaded_files:
                    # img = Image.open(file)
                    st.session_state.files_data.append(("files", (file.name, file.getvalue(), file.type)))
        
        st.write("---") # 分隔線
        # 2. 建立 2 Row x 3 Col 的佈局
        # 第一列 (Row 1)
        r1_col1, r1_col2, r1_col3 = st.columns(3)
        with r1_col1:
            fov_input = st.text_input(label='FOV (nm)', value=1500, disabled=True)
        with r1_col2:
            pitch_x = st.text_input(label='pitch_x', value=45, disabled=True)
        with r1_col3:
            pitch_y = st.text_input(label='pitch_y', value=25.95, disabled=True)

        # 第二列 (Row 2)
        r2_col1, r2_col2, r2_col3 = st.columns(3)
        with r2_col1:
            shrink_thre = st.text_input(label='shrink_thre', value=0.15)
        with r2_col2:
            shift_thre = st.text_input(label='shift_thre', value=4.0)
        with r2_col3:
            close_thre = st.text_input(label='close_thre', value=0.93)

        submitted = st.form_submit_button("🚀 確認並送出")


    if submitted and len(uploaded_files) > 0:
        with st.spinner("辨識中..."):
            try:
                payload = {
                    'fov': int(fov_input),
                    'pitch_x': float(pitch_x),
                    'pitch_y': float(pitch_y),
                    'shrink_thre': float(shrink_thre),
                    'shift_thre': float(shift_thre),
                    'close_thre': float(close_thre)
                }
                
                url = sc_hole_abnormal_app['backend_url']
                url = f"{url}/api/v1/image_processing/sc_hole_abnormal"
                # url = f"http://127.0.0.1:8080/api/v1/image_processing/sc_hole_abnormal"
                response = requests.post(
                    url,
                    files=st.session_state.files_data,
                    data=payload
                )

                # 如果要檢查是否成功
                if response.status_code == 200:
                    results = response.json()
                    st.session_state.files_results = results
                    st.success(f"✅ 完成！ 請前往結果分頁")

                    
                else:
                    st.error(f"❌ 失敗 {response.status_code}")

            except Exception as e:
                err_msg = error_trace_back(e)
                logger.error(err_msg)
                st.error(f"❌ 呼叫 FastAPI 失敗: {e}")

            finally:
                # 清空sessionn
                st.session_state.files_data = []
            
with tab2:
    if st.session_state.files_results is not None:
        result_df = [r['detail'] for r in st.session_state.files_results['data']] 
        result_df = pd.DataFrame(result_df)

        st.dataframe(result_df, height=300)

        result_img1 = [r['img1'] for r in st.session_state.files_results['data']] 
        result_img2 = [r['img2'] for r in st.session_state.files_results['data']] 

        for img_name, i1_b64_str, i2_b64_str in zip(result_df['Image Name'].tolist(), result_img1, result_img2):
            img1 = Image.open(io.BytesIO(base64.b64decode(i1_b64_str))).convert("RGB")
            img2 = Image.open(io.BytesIO(base64.b64decode(i2_b64_str))).convert("RGB")
            
            st.markdown(f"<p style='text-align: center; font-size: 14px; '>{img_name}</p>", unsafe_allow_html=True)
            #st.markdown(f"<h3 style='text-align: center; color: #4F8BF9;'>🖼️ {img_name}</h3>", unsafe_allow_html=True)
            
            _, col1,  _, col2, _ = st.columns([1, 2, 1, 2, 1])
            with col1:
                st.image(img1, use_container_width=True, width=300)

            with col2:
                st.image(img2, use_container_width=True, width=300)




    else:
        st.warning("請先至 \"選擇影像\" 頁籤上傳資料", icon="ℹ️")