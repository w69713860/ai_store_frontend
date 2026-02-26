import numpy as np
import pandas as pd
import typing as ty
import sys, traceback

def summary_dataframe(df: pd.DataFrame) -> ty.Tuple[pd.DataFrame, pd.DataFrame]:
    """
    This function takes a dataframe and returns a summary of the data.
    Arguments:
        df : pd.DataFrame : The dataframe to summarize
        show_plot : bool : If True, show the distribution/bar plot of columns
    Printing:
        the summary of the dataframe by numeric and categorical columns respectively:
        numeric columns summary (mean, std, min, 25%, 50%, 75%, max)
        categorical columns summary (count, unique, top, freq)
    Returns:
        numeric_desc : pd.DataFrame : Summary of numeric columns
        categorical_desc : pd.DataFrame : Summary of categorical columns
    """
    # print("Dataframe shape:", df.shape, "\n")
    # print("Columns:", df.columns.tolist())

    # Get column names by dtype
    numeric_cols = df.select_dtypes(include=['number']).columns
    categorical_cols = df.select_dtypes(include=['object', 'category', 'bool']).columns

    numeric_desc = pd.DataFrame()
    categorical_desc = pd.DataFrame()
    
    # print(f"\nNumerical columns: {len(list(numeric_cols))} cols")
    if not numeric_cols.empty:
        numeric_desc = df[numeric_cols].describe()

    else:
        pass
        # print("No numerical columns found.")

    # print(f"\nCategorical columns: {len(list(categorical_cols))} cols")
    if not categorical_cols.empty:
        categorical_desc = df[categorical_cols].describe(include='all')
    else:
        pass
        # print("No categorical columns found.")
    
    return numeric_desc, categorical_desc



def get_high_na_columns(df:pd.DataFrame, threshold:float=0.3)->ty.List[str]:
    """
    傳回 df 中缺失值比例高於 threshold 的欄位名稱列表。

    參數：
        df (DataFrame): 特徵資料
        threshold (float): 缺失比例門檻，預設為 0.3
    
    回傳：
        List[str]: 欄位名稱列表
    """
    # 計算每個欄位的缺失比例
    na_ratio = df.isna().mean()
    
    # 過濾超過門檻的欄位
    high_na_columns = na_ratio[na_ratio > threshold].index.tolist()
    
    return high_na_columns


def update_unique_list(l: list) -> list:
    return list(set(l))



def error_trace_back(e: Exception) -> str:
    err_type = e.__class__.__name__ # 取得錯誤的class 名稱
    info = e.args[0] # 取得詳細內容
    detains = traceback.format_exc() # 取得完整的tracestack
    n1, n2, n3 = sys.exc_info() #取得Call Stack
    lastCallStack =  traceback.extract_tb(n3)[-1] # 取得Call Stack 最近一筆的內容
    fn = lastCallStack [0] # 取得發生事件的檔名
    lineNum = lastCallStack[1] # 取得發生事件的行數
    funcName = lastCallStack[2] # 取得發生事件的函數名稱
    errMesg = f"FileName: {fn}, lineNum: {lineNum}, Fun: {funcName}, reason: {info}, trace:\n {traceback.format_exc()}"

    return errMesg



def get_source_map(inner:float, outer:float, theta_deg:int, segments:int, rotation_deg:int) -> np.ndarray:
    size=400
    # 轉換角度為弧度
    theta = np.deg2rad(theta_deg)
    rotation = np.deg2rad(rotation_deg)

    # 建立座標網格
    x = np.linspace(-1, 1, size)
    y = np.linspace(-1, 1, size)
    X, Y = np.meshgrid(x, y)

    R = np.sqrt(X**2 + Y**2)
    Phi = np.arctan2(Y, X)  # [-pi, pi]

    # 徑向遮罩 (環狀)
    radial_mask = (R >= inner) & (R <= outer)

    # 角度遮罩 (分段)
    angular_mask = np.zeros_like(R, dtype=bool)

    for k in range(int(segments)):
        phi_center = rotation + k * 2 * np.pi / segments
        dphi = np.angle(np.exp(1j * (Phi - phi_center)))  # wrap to [-pi, pi]
        angular_mask |= (np.abs(dphi) <= theta / 2)

    # 最終光源圖
    source = radial_mask & angular_mask
    return source



