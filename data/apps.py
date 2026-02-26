from wecpy.config_manager import ConfigManager

ConfigManager("config.yaml")

projects = None

if ConfigManager.ENV.IMX_ENV == "DEV":
    projects = [
        {
            "uid": 1,
            "project_name": "SC hole bottom expansion",
            "application_type": "Key Factor Analysis",
            "dev_team": ["TD50", "TD40", "TM20", "TM50"],
            "is_lead": True,
            "desc": "利用AI模型找尋影響製程的關鍵參數。當資料經過適當的整理，此應用會將特徵經過PCA轉換，再使用樹模型進行建模。若模型達到一定的準確率，則可藉由feature importance指標找出關鍵PC參數，再由PCA Loading查找關鍵因子。",
            "data_type": ["tabular data"],
            "page": ["Streamlit", "tabular_sc_bottom_expansion"],
            "backend_url": "http://127.0.0.1:8080",  # dev
            "backend_contributor": None,
            "confluence": "https://confluence.example.com/SC_hole_bottom_expansion",
        },
        {
            "uid": 2,
            "project_name": "SC Hole Abnormal Classification",
            "application_type": "Image Recognition",
            "dev_team": ["TD40"],
            "is_lead": True,
            "desc": "利用影像處理手法自動分析SC Hole Top View 影像，辨識是否存在偏移與縮孔。",
            "data_type": ["image"],
            "page": ["Streamlit", "image_sc_hole_abnormal"],
            "backend_url": "http://127.0.0.1:8080",  # dev
            "backend_contributor": None,
            "confluence": "",
        },
        {
            "uid": 3,
            "project_name": "Litho Source Optimization",
            "application_type": "Parameter Optimization ",
            "dev_team": ["TC10"],
            "is_lead": True,
            "desc": "藉由Litho 光源參數與光罩參數預測Wafer上的曝光強度，並使用最佳化演算法搜索最佳值與對應參數。",
            "data_type": ["tabular data"],
            "page": ["Streamlit", "tabular_litho_source_optimization"],
            "backend_url": "http://127.0.0.1:8080",
            "backend_contributor": None,
            "confluence": "https://confluence.example.com/xxx",
        },
    ]

elif ConfigManager.ENV.IMX_ENV == "PILOT":
    projects = [
        {
            "uid": 1,
            "project_name": "SC Hole Bottom Expansion",
            "application_type": "Key Factor Analysis",
            "dev_team": ["TD50", "TD40", "TM20", "TM50"],
            "is_lead": True,
            "desc": "利用AI模型找尋影響製程的關鍵參數。當資料經過適當的整理，此應用會將特徵經過PCA轉換，再使用樹模型進行建模。若模型達到一定的準確率，則可藉由feature importance指標找出關鍵PC參數，再由PCA Loading查找關鍵因子。",
            "data_type": ["tabular data"],
            "page": ["Streamlit", "tabular_sc_bottom_expansion"],
            "backend_url": "http://ai-store-sc-bottom-expansion-be.fpaip",  # pilot
            "backend_contributor": None,
            "confluence": "https://confluence.example.com/SC_hole_bottom_expansion",
        },
        {
            "uid": 2,
            "project_name": "SC Hole Abnormal Classification",
            "application_type": "Image Recognition",
            "dev_team": ["TD40"],
            "is_lead": True,
            "desc": "利用影像處理手法自動分析SC Hole Top View 影像，辨識是否存在偏移與縮孔。",
            "data_type": ["image"],
            "page": ["Streamlit", "image_sc_hole_abnormal"],
            "backend_url": "http://ai-store-sc-hole-abnormal-be.fpaip",
            "backend_contributor": None,
            "confluence": "",
        },
        {
            "uid": 3,
            "project_name": "Time-series Project",
            "application_type": "Time-series AI (Only for Demo)",
            "dev_team": [],
            "is_lead": True,
            "desc": "AI 模型處理時間序列預測。",
            "data_type": ["tabular data"],
            "page": ["URL", "http://wtli3-test-backend.fpaip/docs/"],
            "backend_url": "http://wtli3-test-backend.fpaip",
            "backend_contributor": None,
            "confluence": "https://confluence.example.com/xxx",
        },
        # {
        #     "uid": 4,
        #     "project_name": "Image Project",
        #     "application_type": "Image Recognition",
        #     "dev_team": [],
        #     "is_lead": False,
        #     "desc": "AI 模型處理影像辨識與分類。",
        #     "data_type": ["image"],
        #     "page": ["Null", ""],
        #     "backend_url": "",
        #     "backend_contributor": None,
        #     "confluence": "https://confluence.example.com/xxx"
        # },
        # {
        #     "uid": 5,
        #     "project_name": "Key Factor Project",
        #     "application_type": "Key Factor Analysis",
        #     "dev_team": [],
        #     "is_lead": False,
        #     "desc": "利用AI模型找尋製程關鍵參數。",
        #     "data_type": ["tabular data"],
        #     "page": ["Null", ""],
        #     "backend_url": "",
        #     "backend_contributor": None,
        #     "confluence": "https://confluence.example.com/xxx"
        # },
        # {
        #     "uid": 6,
        #     "project_name": "Key Factor Project",
        #     "application_type": "Key Factor Analysis (Only for Demo)",
        #     "dev_team": ["TD40"],
        #     "is_lead": True,
        #     "desc": "利用AI模型找尋製程關鍵參數。",
        #     "data_type": ["tabular data"],
        #     "page": ["URL", "http://wtli3-test-backend.fpaip/docs/"],
        #     "backend_url": "http://wtli3-test-backend.fpaip",
        #     "backend_contributor": None,
        #     "confluence": "https://confluence.example.com/xxx"
        # },
    ]


elif ConfigManager.ENV.IMX_ENV == "PROD":
    projects = [
        {
            "uid": 1,
            "project_name": "SC hole bottom expansion",
            "application_type": "Key Factor Analysis",
            "dev_team": ["TD50", "TD40", "TM20", "TM50"],
            "is_lead": True,
            "desc": "利用AI模型找尋影響製程的關鍵參數。當資料經過適當的整理，此應用會將特徵經過PCA轉換，再使用樹模型進行建模。若模型達到一定的準確率，則可藉由feature importance指標找出關鍵PC參數，再由PCA Loading查找關鍵因子。",
            "data_type": ["tabular data"],
            "page": ["Streamlit", "tabular_sc_bottom_expansion"],
            "backend_url": "http://ai-store-sc-bottom-expansion-be.aip",  # prod
            "backend_contributor": None,
            "confluence": "https://confluence.example.com/SC_hole_bottom_expansion",
        },
        {
            "uid": 2,
            "project_name": "SC Hole Abnormal Classification",
            "application_type": "Image Recognition",
            "dev_team": ["TD40"],
            "is_lead": True,
            "desc": "利用影像處理手法自動分析SC Hole Top View 影像，辨識是否存在偏移與縮孔。",
            "data_type": ["image"],
            "page": ["Streamlit", "image_sc_hole_abnormal"],
            "backend_url": "http://ai-store-sc-hole-abnormal-be.aip",
            "backend_contributor": None,
            "confluence": "",
        },
    ]
