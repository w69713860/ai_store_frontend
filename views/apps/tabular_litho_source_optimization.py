import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import requests, json

import plotly.graph_objects as go

from utils.utils import error_trace_back, get_source_map
from data.apps import projects

from wecpy.config_manager import ConfigManager

ConfigManager("config.yaml")
from wecpy.log_manager import LogManager

logger = LogManager.get_logger()

from PIL import Image

litho_source_optimization_app = projects[2]

if "single_if_prediction_result" not in st.session_state:
    st.session_state.single_if_prediction_result = None

if "single_metrics_result" not in st.session_state:
    st.session_state.single_metrics_result = None

st.title("🎯 Parameter Optimization")

st.markdown(
    """
    ### Litho Source Optimization
    藉由Litho 光源參數與光罩參數預測Wafer上的曝光強度，並使用最佳化演算法搜索最佳值與對應參數。
    """
)

tab1, tab2 = st.tabs(
    ["Optimal Patameters Searching", "Prediction"],
    default="Optimal Patameters Searching",
)

with tab1:
    source_mask_option = st.selectbox(
        "Choose a Source & Mask Combination",
        (
            "Dipole Source & Line-Space Mask",
            "Symmetric Source & Contact-Hole Mask",
            "Pixel-Freed Source & Fixed Mask",
        ),
        key="opc_tab1",
    )

    if source_mask_option == "Dipole Source & Line-Space Mask":
        image = Image.open(
            "assets/tabular_litho_source_optimization/Dipole_Source_Line-Space_Mask.png"
        )  # 換成你的圖片路徑
        st.image(image, use_container_width=False, width=600)

        with st.form("tab1_input_form"):

            st.subheader("光源參數")
            s_r1c1, s_r1c2, s_r1c3, s_r1c4 = st.columns(4)

            with s_r1c1:
                nas = st.slider(
                    "Select a range of NA", 1.3, 1.35, (1.3, 1.35), step=0.05
                )
            with s_r1c2:
                theta = st.slider("Select a range of Theta", 20, 80, (20, 80), step=10)
            with s_r1c3:
                inner = st.slider(
                    "Select a range of Inner", 0.5, 0.8, (0.5, 0.8), step=0.05
                )
            with s_r1c4:
                outer = st.slider(
                    "Select a range of Outer", 0.83, 0.98, (0.83, 0.98), step=0.01
                )

            st.write("---")  # 分隔線

            st.subheader("強度閥值")
            threshold = st.slider(
                "Select a range of Threshold",
                0.05,
                0.35,
                (0.05, 0.35),
                step=0.015,
                format="%.3f",
            )
            st.write("---")  # 分隔線

            st.subheader("光罩參數")

            m_col1, m_col2, m_col3, _ = st.columns(4)
            with m_col1:
                mask_width = st.slider(
                    label="Mask Width",
                    value=(40, 50),
                    min_value=36,
                    max_value=60,
                    step=2,
                )
            with m_col2:
                mask_space = st.slider(
                    label="Mask Space",
                    value=(40, 50),
                    min_value=36,
                    max_value=60,
                    step=2,
                )
            st.write("---")  # 分隔線

            st.subheader("最佳參數搜索")
            # threshold = st.slider("Select a range of Threshold", 0.05, 0.35, (0.05, 0.35), step=0.015, format="%.3f")
            st.markdown(
                """
                #### Objective 
                """
            )
            o_r1c1, o_r1c2, o_r1c3, _ = st.columns(4)

            with o_r1c1:
                contrast_o = st.selectbox("Contrast", ["Max", "min"], 0, disabled=True)
                if contrast_o == "Max":
                    contrast_v = st.slider(
                        "Lower Bound",
                        0.1,
                        1.0,
                        0.5,
                        step=0.1,
                        format="%.2f",
                        disabled=True,
                    )
                if contrast_o == "min":
                    contrast_v = st.slider(
                        "Upper Bound",
                        0.1,
                        1.0,
                        0.5,
                        step=0.1,
                        format="%.2f",
                        disabled=True,
                    )

            with o_r1c2:
                ils_o = st.selectbox("ILS", ["Max", "min"], 0, disabled=True)
                if ils_o == "Max":
                    ils_v = st.slider(
                        "Lower Bound",
                        0.0,
                        100.0,
                        23.0,
                        step=0.1,
                        format="%.1f",
                        disabled=True,
                    )
                if ils_o == "Min":
                    ils_v = st.slider(
                        "Upper Bound",
                        0.0,
                        100.0,
                        23.0,
                        step=0.1,
                        format="%.1f",
                        disabled=True,
                    )

            with o_r1c3:
                width_o = st.selectbox("Width (um)", ["in Range"], 0, disabled=True)
                width_v = st.slider(
                    "Range",
                    0.03,
                    0.05,
                    (0.038, 0.042),
                    step=0.001,
                    format="%.3f",
                    disabled=True,
                )

            st.markdown("""#### Trial""")
            o_r3c1, o_r3c2, _, _ = st.columns(4)
            with o_r3c1:
                rotation = st.number_input(
                    label="嘗試次數",
                    value=1500,
                    min_value=1000,
                    max_value=2000,
                    step=100,
                    placeholder="Type a number...",
                )
            with o_r3c2:
                keeps = st.number_input(
                    label="保留最好結果數",
                    value=50,
                    min_value=10,
                    max_value=100,
                    step=10,
                    placeholder="Type a number...",
                )

            submitted = st.form_submit_button("🚀 搜尋")

        if submitted:
            import pandas as pd

            result_df = pd.read_csv("./only_dev/searching_results.csv")
            result_df["Score"] = (
                result_df["Ils"] + result_df["Nils"] + result_df["Contrast"]
            )

            st.session_state["result_df"] = result_df

        if "result_df" in st.session_state:
            result_df = st.session_state["result_df"]
            st.subheader("搜索結果")

            with st.container():
                col1, col2 = st.columns([3, 2])

                with col1:
                    event = st.dataframe(
                        result_df[
                            [
                                "NA",
                                "Polar_Alpha",
                                "Polar_Degree",
                                "Segments",
                                "Rotation",
                                "Theta",
                                "Inner",
                                "Outer",
                                "Threshold",
                                "Score",
                            ]
                        ],
                        height=800,
                        use_container_width=True,
                        selection_mode="single-row",  # ✅ 新 API
                        on_select="rerun",
                    )

                with col2:
                    if event and event.selection.rows:
                        idx = event.selection.rows[0]
                        selected_row = result_df.iloc[idx]

                        ## Source Map
                        st.markdown("### 📈 Selected Source Map")
                        source_map = get_source_map(
                            selected_row["Inner"],
                            selected_row["Outer"],
                            int(selected_row["Theta"]),
                            int(selected_row["Segments"]),
                            int(selected_row["Rotation"]),
                        )

                        fig = px.imshow(
                            source_map,
                            color_continuous_scale="gray",  # 設定為灰階
                            origin="lower",  # 設定原點在左下角 (視你的資料結構而定)
                            labels=dict(color="Intensity"),  # 標籤名稱
                        )

                        # 優化圖表佈局
                        fig.update_layout(
                            height=400,
                            width=400,
                            # coloraxis_showscale=True,      # 顯示右側顏色條
                            margin=dict(l=10, r=10, t=10, b=10),
                            xaxis_title="X Axis",
                            yaxis_title="Y Axis",
                        )

                        # 在 Streamlit 中顯示
                        st.plotly_chart(fig, use_container_width=True)

                        # 1. 取得強度函數數據 (100個點)
                        intensity_function = (
                            selected_row[[f"IF{i+1}" for i in range(100)]]
                            .astype(float)
                            .values
                        )
                        threshold = selected_row["Threshold"]
                        metrics = selected_row[["Width", "Ils", "Nils", "Contrast"]]

                        st.markdown("### 📈 Selected Intensity Profile")

                        df_plot = pd.DataFrame(
                            {
                                "Position": range(len(intensity_function)),
                                "Intensity": intensity_function,
                            }
                        )

                        # 3. 使用 plotly.px 畫出主曲線
                        fig = px.line(
                            df_plot,
                            x="Position",
                            y="Intensity",
                            title=f"Intensity Profile (Threshold: {threshold:.4f})",
                            labels={
                                "Position": "Position (index)",
                                "Intensity": "Intensity Value",
                            },
                        )

                        # 4. 加入 Threshold 水平線
                        fig.add_hline(
                            y=threshold,
                            line_dash="dash",
                            line_color="red",
                            annotation_text=f"Threshold: {threshold:.4f}",
                            annotation_position="bottom right",
                        )

                        # 5. 優化佈局：在圖上以註解方式顯示更多 Metrics (選用)
                        metrics_text = (
                            f"Width: {metrics['Width']:.4f}<br>"
                            f"ILS: {metrics['Ils']:.4f}<br>"
                            f"NILS: {metrics['Nils']:.4f}<br>"
                            f"Contrast: {metrics['Contrast']:.4f}"
                        )

                        fig.add_annotation(
                            xref="paper",
                            yref="paper",
                            x=0.02,
                            y=0.98,
                            text=metrics_text,
                            showarrow=False,
                            align="left",
                            bgcolor="rgba(255, 255, 255, 0.7)",
                            bordercolor="gray",
                            borderwidth=1,
                        )
                        # 優化圖表佈局
                        fig.update_layout(
                            height=300,
                            width=400,
                            margin=dict(l=10, r=10, t=30, b=10),
                        )

                        # 6. 在 Streamlit 顯示圖表
                        st.plotly_chart(fig, use_container_width=True)

                        # # 📊 Metrics
                        # c1, c2, c3, c4 = st.columns(4)
                        # c1.markdown(
                        #     f"""
                        #     <div style="text-align:center;">
                        #         <div style="font-size:14px; color: #6b7280;">Width</div>
                        #         <div style="font-size:20px; font-weight:600;">{metrics['Width']:.6f}</div>
                        #     </div>
                        #     """,
                        #     unsafe_allow_html=True
                        # )

                    else:
                        st.info("👈 請在左邊點選一筆資料")

    if source_mask_option == "Symmetric Source & Contact-Hole Mask":
        st.subheader("尚未開放")

    if source_mask_option == "Pixel-Freed Source & Fixed Mask":
        st.subheader("尚未開放")


with tab2:
    source_mask_option = st.selectbox(
        "Choose a Source & Mask Combination",
        (
            "Dipole Source & Line-Space Mask",
            "Symmetric Source & Contact-Hole Mask",
            "Pixel-Freed Source & Fixed Mask",
        ),
        key="opc_tab2",
    )

    if source_mask_option == "Dipole Source & Line-Space Mask":
        image = Image.open(
            "assets/tabular_litho_source_optimization/Dipole_Source_Line-Space_Mask.png"
        )  # 換成你的圖片路徑
        st.image(image, use_container_width=False, width=600)

        with st.form("tab2_input_form"):

            st.subheader("光源參數")

            s_r1c1, s_r1c2, s_r1c3, s_r1c4 = st.columns(4)
            with s_r1c1:
                na = st.slider("Select a value of NA", 1.05, 1.35, 1.3, step=0.05)
            with s_r1c2:
                theta = st.slider("Select a value of Theta", 20, 80, 30, step=10)
            with s_r1c3:
                inner = st.slider("Select a value of Inner", 0.5, 0.8, 0.7, step=0.05)
            with s_r1c4:
                outer = st.slider(
                    "Select a value of Outer", 0.83, 0.98, 0.90, step=0.03
                )

            st.subheader("光罩參數")

            m_col1, m_col2, _, _ = st.columns(4)
            with m_col1:
                mask_width = st.slider(
                    "Select a value of Mask Width", 36, 60, 40, step=2
                )
            with m_col2:
                mask_space = st.slider(
                    "Select a value of Mask Space", 36, 60, 40, step=2
                )

            submitted = st.form_submit_button("🚀 預測")
            if submitted:
                st.session_state.single_if_prediction_result = None
                st.session_state.single_metrics_result = None
                with st.spinner("模型預測中..."):
                    try:
                        payload = {
                            "source_mask_type": source_mask_option,
                            "mask_width": mask_width,
                            "mask_space": mask_space,
                            "na": na,
                            "theta": theta,
                            "inner": inner,
                            "outer": outer,
                        }

                        url = litho_source_optimization_app["backend_url"]
                        url = f"{url}/api/v1/opc_litho_optimize/inference"

                        logger.info(f"post model inference api")

                        response = requests.post(
                            url,
                            data=json.dumps(payload, allow_nan=True),  # 強制允許 NaN
                            headers={"Content-Type": "application/json"},
                        )

                        # 如果要檢查是否成功
                        if response.status_code == 200:
                            result = response.json()
                            st.success(f"✅ 完成！ ")
                            st.session_state.single_if_prediction_result = result[
                                "data"
                            ]

                        elif response.status_code == 400:
                            result = response.json()
                            logger.error(result["detail"])
                            st.error(f"❌ 預測失敗！{result['detail']}")

                        else:
                            # logger.error('模型訓練失敗，請確認所選數據！')
                            st.error(f"❌ 錯誤! {response.status_code}")

                    except Exception as e:
                        err_msg = error_trace_back(e)
                        logger.error(err_msg)
                        st.error(f"❌ 呼叫 FastAPI 失敗: {e}")

        if st.session_state.single_if_prediction_result is not None:
            result = st.session_state.single_if_prediction_result

            prediction_r1c1, prediction_r1c2 = st.columns(2)

            with prediction_r1c1:
                st.subheader("📈 Predicted Intensity Function")
                intensity = result["intensity"]

                # threshold slider
                threshold = st.slider(
                    "Threshold",
                    min_value=0.0,
                    max_value=0.6,
                    value=0.1,
                    step=0.01,
                )

                # === Plot ===
                fig = go.Figure()
                # intensity curve
                fig.add_trace(
                    go.Scatter(
                        x=np.arange(len(intensity)),
                        y=intensity,
                        mode="lines",
                        name="Intensity",
                    )
                )

                # threshold horizontal line
                fig.add_hline(
                    y=threshold,
                    line_dash="dash",
                    line_color="red",
                    annotation_text=f"Threshold = {threshold:.2f}",
                    annotation_position="top left",
                )

                fig.update_layout(
                    height=400,
                    margin=dict(l=20, r=20, t=40, b=20),
                    xaxis_title="Index",
                    yaxis_title="Intensity",
                )
                fig.update_yaxes(range=[0, 0.6])

                st.plotly_chart(fig, use_container_width=True)

                calculate_metrics_button = st.button(
                    "Calculate Metrics", key="calculate_metrics_button"
                )

                if calculate_metrics_button:
                    payload = {
                        "intensity": intensity,
                        "threshold": threshold,
                        "dx": result["dx_new"],
                    }

                    url = litho_source_optimization_app["backend_url"]
                    url = f"{url}/api/v1/opc_litho_optimize/calculate"

                    logger.info(f"post calculate api")

                    response = requests.post(
                        url,
                        data=json.dumps(payload, allow_nan=True),  # 強制允許 NaN
                        headers={"Content-Type": "application/json"},
                    )

                    # 如果要檢查是否成功
                    if response.status_code == 200:
                        result = response.json()
                        st.session_state.single_metrics_result = result["data"]

                    elif response.status_code == 400:
                        result = response.json()
                        logger.error(result["detail"])
                        st.error(f"❌ 計算失敗！{result['detail']}")

                    else:
                        # logger.error('模型訓練失敗，請確認所選數據！')
                        st.error(f"❌ 錯誤! {response.status_code}")

            if st.session_state.single_metrics_result is not None:
                metrics_result = st.session_state.single_metrics_result

                with prediction_r1c2:
                    st.subheader("📊 Metrics Result")

                    metric_c1, metric_c2, metric_c3, metric_c4 = st.columns(4)
                    metric_c1.markdown(
                        f"""
                        <div style="text-align:center;">
                            <div style="font-size:14px; color: #6b7280;">Width</div>
                            <div style="font-size:20px; font-weight:600;">{metrics_result['width']:.6f}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    metric_c2.markdown(
                        f"""
                        <div style="text-align:center;">
                            <div style="font-size:14px; color: #6b7280;">ILS</div>
                            <div style="font-size:20px; font-weight:600;">{metrics_result['ils']:.6f}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    metric_c3.markdown(
                        f"""
                        <div style="text-align:center;">
                            <div style="font-size:14px; color: #6b7280;">NILS</div>
                            <div style="font-size:20px; font-weight:600;">{metrics_result['nils']:.6f}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    metric_c4.markdown(
                        f"""
                        <div style="text-align:center;">
                            <div style="font-size:14px; color: #6b7280;">Contrast</div>
                            <div style="font-size:20px; font-weight:600;">{metrics_result['contrast']:.6f}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

    if source_mask_option == "Symmetric Source & Contact-Hole Mask":
        st.subheader("尚未開放")

    if source_mask_option == "Pixel-Freed Source & Fixed Mask":
        st.subheader("尚未開放")
