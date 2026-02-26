import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import requests, json

from utils.utils import summary_dataframe, error_trace_back, update_unique_list
from data.apps import projects

from wecpy.config_manager import ConfigManager
ConfigManager('config.yaml')
from wecpy.log_manager import LogManager
logger = LogManager.get_logger()

# TODO 加入檔案限制 (20 Mb)

key_factor_analysis_app = projects[0]

df_raw = None

if 'df_preproc' not in st.session_state:
    st.session_state.df_preproc = None

if 'analysis_report' not in st.session_state:
    st.session_state.analysis_report = None

# if 'selected_features' not in st.session_state:
#     st.session_state.selected_features = []

# df_preproc = None
# analysis_report = None

st.title("🔑 Key Factor Analysis")
st.markdown("""
    ### SC Hole Bottom Expansion Key Factor Analysis
    製程關鍵因子分析。
    """)


tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["Data Preparation", "Data Visualization", "Data Preprocessing", "Modeling", "Key Factor Analysis"], default="Data Preparation"
)

with tab1:
    uploaded_file = st.file_uploader("請上傳 CSV 檔案", accept_multiple_files=False, type="csv")
    if uploaded_file is not None:
        df_raw = pd.read_csv(uploaded_file)
        rows, columns = df_raw.shape
        logger.info(f"上傳 {uploaded_file} 檔案成功")
        st.caption(f"資料筆數: {rows} ; 資料欄位: {columns}")
        st.dataframe(df_raw)

        
with tab2:
    if df_raw is not None:
        numeric_desc, categorical_desc = summary_dataframe(df_raw)
        st.subheader("數值型欄位資訊")
        st.dataframe(numeric_desc)

        st.subheader("類別型欄位資訊")
        st.dataframe(categorical_desc)

        st.subheader("數據分佈圖")
        # 讓使用者選擇欄位
        numeric_cols = df_raw.select_dtypes(include=["int", "float"]).columns.tolist()
        categorical_cols = df_raw.select_dtypes(exclude=["int", "float"]).columns.tolist()

        selected_cols_dist = st.multiselect("選擇要查看的欄位（可多選）：", df_raw.columns.tolist())
        # ------------------------------
        # 繪圖區域
        # ------------------------------
        if not selected_cols_dist:
            st.warning("請至少選擇一個欄位。")
        else:
            # 容器包起來
            with st.container():
                # 每 3 欄為一列
                cols_per_row = 3
                for i in range(0, len(selected_cols_dist), cols_per_row):
                    cols = st.columns(cols_per_row)
                    for j, col_name in enumerate(selected_cols_dist[i:i + cols_per_row]):
                        with cols[j]:
                            # 數值欄位 → histogram
                            if col_name in numeric_cols:
                                fig = px.histogram(
                                    df_raw,
                                    x=col_name,
                                    nbins=30,
                                    title=f"{col_name} 分佈",
                                    color_discrete_sequence=["#1677ff"]
                                )
                                fig.update_layout(
                                    height=300,
                                    margin=dict(l=20, r=20, t=40, b=20)
                                )
                                st.plotly_chart(fig, use_container_width=True)
                            
                            # 類別欄位 → bar chart
                            elif col_name in categorical_cols:
                                fig = px.bar(
                                    df_raw[col_name].value_counts().reset_index(),
                                    x=col_name,
                                    y="count",
                                    title=f"{col_name} 類別統計",
                                    color_discrete_sequence=["#ffa940"]
                                )
                                fig.update_layout(
                                    height=300,
                                    margin=dict(l=20, r=20, t=40, b=20)
                                )
                                st.plotly_chart(fig, use_container_width=True)

        st.subheader("缺失值總覽")
        na_df = df_raw.isna()
        na_numeric = na_df.astype(int)
        na_summary = na_numeric.mean().to_frame().reset_index(drop=False)
        # na_summary = na_summary.rename(columns={'index': 'features', 0: 'missing_ratio'})
        na_summary.columns = ['features', 'missing_ratio']
        
        # 容器包起來
        with st.container():
            # 每 2 欄為一列
            cols_per_row = 2
            cols = st.columns(cols_per_row)

            with cols[0]:
            ## na heatmap
                fig = px.imshow(
                    na_numeric,  # 轉置讓欄位在 Y 軸，比較直覺
                    color_continuous_scale=["#1677ff", "#ff4d4f"],  # 藍(無缺) → 紅(有缺)
                    labels=dict(x="Columns", y="Row Index", color="是否缺失 (1=缺失)"),
                    title="Missing Value Heatmap"
                )
                # 格式微調
                fig.update_layout(
                    height=600,
                    width=400,
                    margin=dict(l=50, r=50, t=80, b=50),
                    xaxis=dict(
                        showgrid=False,
                        #autorange="reversed", ## 保持排列順序
                        tickmode="array",
                        tickvals=list(range(len(na_numeric.columns))),
                        ticktext=[c[:15] + "..." if len(c) > 15 else c for c in na_numeric.columns]  # ✅ 太長就截斷
                        ),
                    yaxis=dict(showgrid=False) 
                )
                st.plotly_chart(fig, use_container_width=True)

            with cols[1]:
                fig = px.bar(
                    na_summary,
                    x="features",
                    y="missing_ratio",
                    title=f"缺失值統計",
                    color_discrete_sequence=["#ffa940"]
                )
                fig.update_layout(
                    height=600,
                    width=400,
                    margin=dict(l=50, r=50, t=80, b=50),
                    xaxis=dict(
                        showgrid=False,
                        #autorange="reversed", ## 保持排列順序
                        tickmode="array",
                        tickvals=list(range(len(na_numeric.columns))),
                        ticktext=[c[:15] + "..." if len(c) > 15 else c for c in na_numeric.columns]  # ✅ 太長就截斷
                        ),
                    yaxis=dict(showgrid=False) 
                    
                )
                st.plotly_chart(fig, use_container_width=True)


        st.subheader("相關係數矩陣")
        selected_cols_corr = st.multiselect("選擇要計算相關係數的欄位：", numeric_cols, default=numeric_cols)
        if selected_cols_corr:
            corr = df_raw[selected_cols_corr].corr()
            st.subheader("🔥 相關係數熱力圖")
            fig = px.imshow(
                corr,
                text_auto=".2f",              # 顯示數值
                color_continuous_scale="RdBu_r",  # 紅藍反轉配色
                title="Correlation Heatmap",
                aspect="auto"
            )
            fig.update_layout(
                width=700,
                height=600,
                margin=dict(l=50, r=50, t=80, b=50),
                xaxis=dict(
                        showgrid=False,
                        tickmode="array",
                        tickvals=list(range(len(corr.columns))),
                        ticktext=[c[:15] + "..." if len(c) > 15 else c for c in corr.columns]  # ✅ 太長就截斷
                    ),
                yaxis=dict(
                        showgrid=False,
                        tickmode="array",
                        tickvals=list(range(len(corr.columns))),
                        ticktext=[c[:15] + "..." if len(c) > 15 else c for c in corr.columns]  # ✅ 太長就截斷
                    ),
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("請至少選擇一個數值欄位。")

        

    else:
        st.warning("請先至 Data Preparation 頁籤上傳資料", icon="ℹ️")


with tab3:
    if df_raw is not None:
        numeric_cols = df_raw.select_dtypes(include=["int", "float"]).columns.tolist()
        categorical_cols = df_raw.select_dtypes(exclude=["int", "float"]).columns.tolist()
        rows, columns = df_raw.shape
        
        st.caption(f"原始資料筆數: {rows} ; 資料欄位: {columns}")
        # 使用 form
        with st.form("preprocess_form"):
            st.subheader("欄位選擇")
            selected_cols_numeric = st.multiselect("選擇要處理的欄位(數值)", numeric_cols, default=numeric_cols)
            selected_cols_category = st.multiselect("選擇要處理的欄位(類別)", categorical_cols, default=categorical_cols)

            st.subheader("缺失值處理(數值)")
            na_method_numeric = st.selectbox("選擇缺失值處理方式", ["Mean", "Mediam"])

            st.subheader("缺失值處理(類別)")
            na_method_category = st.selectbox("選擇缺失值處理方式", ["Mode"], index=0, disabled=True)

            submitted = st.form_submit_button("🚀 確認並送出")

        if submitted:
            logger.info(f'submited preprocessing form')
            logger.info(f'clear st.session_state.analysis_report')
            st.session_state.df_preproc = None

            with st.spinner("處理中..."):
                try:
                    payload = {
                        "na_method_numeric": na_method_numeric,
                        "na_method_category": na_method_category,
                        "selected_cols_numeric": selected_cols_numeric,
                        "selected_cols_category": selected_cols_category,
                        "dataframe": df_raw.to_dict(orient="records")
                    }
                    
                    url = key_factor_analysis_app['backend_url']
                    url = f"{url}/api/v1/key_factor_analysis/data_preprocessing"
                    response = requests.post(
                        url,
                        data=json.dumps(payload, allow_nan=True),  # 強制允許 NaN
                        headers={"Content-Type": "application/json"}
                    )
                    # response = requests.post(url, json=payload)
                    # url = f"http://127.0.0.1:10117"
                    # response = requests.get(url)

                    # 如果要檢查是否成功
                    if response.status_code == 200:
                        result = response.json()
                        st.success(f"✅ 前處理完成！ 請前往Modeling頁籤")

                        df_preproc = pd.DataFrame(result['data']['dataframe'])
                        r, c = df_preproc.shape
                        st.caption(f"處理後資料筆數: {r} ; 資料欄位: {c}")
                        st.dataframe(df_preproc, height=400)

                        ## 塞回session
                        st.session_state.df_preproc = df_preproc

                        na_df = df_preproc.isna()
                        na_numeric = na_df.astype(int)
                        na_summary = na_numeric.mean().to_frame().reset_index(drop=False)
                        # na_summary = na_summary.rename(columns={'index': 'features', 0: 'missing_ratio'})
                        na_summary.columns = ['features', 'missing_ratio']
                        
                        # 容器包起來
                        with st.container():
                            # 每 2 欄為一列
                            cols_per_row = 2
                            cols = st.columns(cols_per_row)

                            with cols[0]:
                            ## na heatmap
                                fig = px.imshow(
                                    na_numeric,  # 轉置讓欄位在 Y 軸，比較直覺
                                    color_continuous_scale=["#1677ff", "#ff4d4f"],  # 藍(無缺) → 紅(有缺)
                                    labels=dict(x="Columns", y="Row Index", color="是否缺失 (1=缺失)"),
                                    title="Missing Value Heatmap"
                                )
                                # 格式微調
                                fig.update_layout(
                                    height=600,
                                    width=400,
                                    margin=dict(l=50, r=50, t=80, b=50),
                                    xaxis=dict(
                                        showgrid=False,
                                        #autorange="reversed", ## 保持排列順序
                                        tickmode="array",
                                        tickvals=list(range(len(na_numeric.columns))),
                                        ticktext=[c[:15] + "..." if len(c) > 15 else c for c in na_numeric.columns]  # ✅ 太長就截斷
                                        ),
                                    yaxis=dict(showgrid=False) 
                                )
                                st.plotly_chart(fig, use_container_width=True, key = 'tab3-0')

                            with cols[1]:
                                fig = px.bar(
                                    na_summary,
                                    x="features",
                                    y="missing_ratio",
                                    title=f"缺失值統計",
                                    color_discrete_sequence=["#ffa940"]
                                )
                                fig.update_layout(
                                    height=600,
                                    width=400,
                                    margin=dict(l=50, r=50, t=80, b=50),
                                    xaxis=dict(
                                        showgrid=False,
                                        #autorange="reversed", ## 保持排列順序
                                        tickmode="array",
                                        tickvals=list(range(len(na_numeric.columns))),
                                        ticktext=[c[:15] + "..." if len(c) > 15 else c for c in na_numeric.columns]  # ✅ 太長就截斷
                                        ),
                                    yaxis=dict(showgrid=False) 
                                    
                                )
                                st.plotly_chart(fig, use_container_width=True, key = 'tab3-1')
                    
                    
                    elif response.status_code == 400:
                        result = response.json()
                        logger.error(result)
                        st.error(f"❌ 前處理失敗！ {result['detail']}")

                    else:
                        st.error(f"❌ 前處理失敗，請確認數據！{response.status_code}")
                        #print(f"Request failed with status code: {response.status_code}")
          

                except Exception as e:
                    err_msg = error_trace_back(e)
                    logger.error(err_msg)
                    st.error(f"❌ 呼叫 FastAPI 失敗: {err_msg}")

    else:
        st.warning("請先至 Data Preparation 頁籤上傳資料", icon="ℹ️")
    

with tab4:
    if df_raw is not None:
        if st.session_state.df_preproc is not None:
            all_columns = st.session_state.df_preproc.columns.tolist()
            numeric_cols = st.session_state.df_preproc.select_dtypes(include=["int", "float"]).columns.tolist()
            categorical_cols = st.session_state.df_preproc.select_dtypes(exclude=["int", "float"]).columns.tolist()
            
            # 使用 form
            with st.form("Modeling"):
                st.subheader("選擇任務")
                selected_task = st.selectbox("任務", options=["Classification", "Regression"], index=0)

                st.subheader("Y欄位選擇")
                selected_y_col = st.selectbox("選擇Y欄位", all_columns)

                st.subheader("X欄位選擇，僅能選擇數值型欄位")
                selected_x_cols = st.multiselect("選擇X欄位(數值)", numeric_cols, default=numeric_cols)

                st.subheader("PCA Dimension Reduction")
                # is_pca = st.checkbox("是否使用Principle Component Features", value=True, disabled =True)
                is_pca = st.checkbox("是否使用Principle Component Features", value=True)

                submitted = st.form_submit_button("🚀 確認並送出")

            if submitted:
                logger.info(f'submited modeling form')
                logger.info(f'clear st.session_state.analysis_report')
                st.session_state.analysis_report = None
                
                with st.spinner("模型訓練中..."):
                    try:
                        payload = {
                            'dataframe': st.session_state.df_preproc.to_dict(orient="records"),
                            'task': selected_task,
                            'y_col': selected_y_col,
                            'x_cols': selected_x_cols,
                            'is_pca': is_pca
                        }
                        
                        url = key_factor_analysis_app['backend_url']
                        url = f"{url}/api/v1/key_factor_analysis/modeling"
                        
                        logger.info(f'post model training api')
                        response = requests.post(
                            url,
                            data=json.dumps(payload, allow_nan=True),  # 強制允許 NaN
                            headers={"Content-Type": "application/json"}
                        )

                        # 如果要檢查是否成功
                        if response.status_code == 200:
                            result = response.json()
            
                            st.success(f"✅ 模型訓練完成！ 請前往Key Factor Analysis頁籤")
                            st.session_state.analysis_report = result['data']

                        elif response.status_code == 400:
                            result = response.json()
                            logger.error(result['detail'])
                            st.error(f"❌ 模型訓練失敗！{result['detail']}")

                        else:
                            logger.error('模型訓練失敗，請確認所選數據！')
                            st.error(f"❌ 模型訓練失敗，請確認所選數據！{response.status_code}")


                    
                    except Exception as e:
                        err_msg = error_trace_back(e)
                        logger.error(err_msg)
                        st.error(f"❌ 呼叫 FastAPI 失敗: {e}")

        else:
            st.warning("請先至 Data Preprocessing 頁籤進行資料整理", icon="ℹ️")           

    else:
        st.warning("請先至 Data Preparation 頁籤上傳資料", icon="ℹ️")


with tab5:
    if df_raw is not None:
        if st.session_state.analysis_report is not None:
            analysis_report_ = st.session_state.analysis_report.copy()

            if analysis_report_["task"] == 'Classification':
                st.subheader(f"Model Performance (Accuracy): {analysis_report_['result']['model_performance'] * 100:.2f}%")
                
                testing_set = pd.DataFrame(analysis_report_['result']['testing_set'])
                confusion_matrix = analysis_report_['result']['confusion_matrix'] # {'matrix': [], 'labels':[]}

                with st.container():
                    col1, col2 = st.columns([1, 1])

                    with col1:
                        st.subheader("Testing Set")
                        st.dataframe(testing_set, use_container_width=True, height=400)

                    with col2:
                        st.subheader("Confusion Matrix")

                        labels = confusion_matrix["labels"]
                        cm_df = pd.DataFrame(
                            confusion_matrix["matrix"],
                            index=[f"True {l}" for l in labels],
                            columns=[f"Pred {l}" for l in labels]
                        )

                        fig = px.imshow(
                            cm_df, text_auto=True,
                            color_continuous_scale="Blues", aspect="auto"
                        )
                        
                        fig.update_layout(
                            xaxis_title="Predicted Label", yaxis_title="True Label",
                            coloraxis_colorbar=dict(title="Count")
                        )

                        st.plotly_chart(fig, use_container_width=True)
            
            if analysis_report_["task"] == 'Regression':
                st.subheader(f"Model Performance (R-square): {analysis_report_['result']['model_performance'] * 100:.2f}%")

                testing_set = pd.DataFrame(analysis_report_['result']['testing_set'])

                with st.container():
                    col1, col2 = st.columns([1, 1])

                    with col1:
                        st.subheader("Testing Set")
                        st.dataframe(testing_set, use_container_width=True, height=400)

                    with col2:
                        st.subheader("Ground True vs. Prediction")

                        # 組 dataframe（方便之後擴充 hover）
                        y_col = analysis_report_['y_col']
                        df_plot = pd.DataFrame({
                            "y_true": testing_set[y_col],
                            "y_pred": testing_set['Prediction']
                        })

                        # 對角線範圍
                        min_val = min(df_plot.min())
                        max_val = max(df_plot.max())

                        fig = px.scatter(
                            df_plot, x="y_true", y="y_pred",
                            labels={
                                "y_true": "True Value",
                                "y_pred": "Predicted Value"
                            },
                            title="True vs. Predicted"
                        )

                        # 加上 y = x 對角線
                        fig.add_shape(
                            type="line",
                            x0=min_val, y0=min_val,
                            x1=max_val, y1=max_val,
                            line=dict(
                                dash="dash"
                            )
                        )
                        st.plotly_chart(fig, use_container_width=True)

            
            st.divider()
            # 容器包起來
            st.subheader(f"Key Factor Analysis: ")

            with st.container():
                # 每 2 欄為一列
                cols_per_row = 2
                cols = st.columns(cols_per_row)

                with cols[0]:
                    feature_importance = pd.DataFrame(analysis_report_['result']['feature_importance'])
                    feature_importance = feature_importance.sort_values(by=['importance'], ascending=False).head(20)
                   
                    ## feature importance bar chart
                    fig = px.bar(
                        feature_importance,
                        x="importance",
                        y="feature",
                        title=f"Feature Importance",
                        color_discrete_sequence=["#ffa940"]
                    )
                    # 格式微調
                    fig.update_layout(
                        height=600,
                        width=400,
                        margin=dict(l=10, r=10, t=20, b=20),
                        yaxis=dict(
                            showgrid=False,
                            autorange="reversed", ## 保持排列順序
                            tickmode="array",
                            tickvals=feature_importance['feature'],
                            ticktext=[c[:15] + "..." if len(c) > 15 else c for c in feature_importance['feature']]  # ✅ 太長就截斷
                            ),
                        xaxis=dict(showgrid=False) 
                    )
                    st.plotly_chart(fig, use_container_width=True, key = 'tab5-0')

                with cols[1]:
                    if analysis_report_['is_pca']:
                        # pca_loading_matrix
                        pca_loading_matrix = pd.DataFrame(
                            analysis_report_['result']['pca_loading_matrix'],
                            index=analysis_report_['result']['pca_loading_index']
                        )

                        # 建立水平排列的欄位
                        param_cols = st.columns(2)
                        with param_cols[0]:
                            selected_pc = st.selectbox("選擇PC查看關鍵參數", pca_loading_matrix.columns.tolist(), index=0)
                        with param_cols[1]:
                            top_k = st.selectbox("TOP K 相關參數", [i+1 for i in range(pca_loading_matrix.shape[0])], index=0)

                        # 取出該 PC 欄位 & 排序
                        pc_loading = pca_loading_matrix[selected_pc].abs().sort_values(ascending=False)

                        # 選擇前 top_k 個參數
                        top_features = pc_loading.head(top_k).index
                        filtered_df = pca_loading_matrix.loc[top_features, [selected_pc]]

                        # 顯示結果
                        st.write(f"📊 Top {top_k} 關鍵參數對 {selected_pc} 的貢獻：")
                        
                        st.dataframe(filtered_df.style.format("{:.4f}"))

                        
        else:
            st.warning("請先至 Modeling 頁籤訓練模型", icon="ℹ️")
            
    else:
        st.warning("請先至 Data Preparation 頁籤上傳資料", icon="ℹ️")


