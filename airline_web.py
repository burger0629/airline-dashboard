import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from scipy.optimize import minimize
import datetime
import requests
import time
from geopy.geocoders import Nominatim
import feedparser  

from auth_system import setup_authenticator 

# ==========================================
# 0. 網頁基本設定 
# ==========================================
st.set_page_config(page_title="航空公司營運戰情室 (God Mode)", layout="wide", initial_sidebar_state="expanded")

# ==========================================
# 1. 系統登入大門 
# ==========================================
authenticator, config = setup_authenticator()
st.subheader("🛡️ 航空戰情室 - 企業級安全登入")

authenticator.login(location="main")

if st.session_state.get("authentication_status") is False:
    st.error("❌ 識別碼或通行密碼錯誤，拒絕存取。")
elif st.session_state.get("authentication_status") is None:
    st.warning("⚠️ 系統已鎖定，請輸入高階主管識別碼以進入 God Mode 戰情室。")
    st.info("💡 測試帳號：`commander_lin` / 密碼：`123456`")
elif st.session_state.get("authentication_status"):
    
    # ==========================================
    # 2. 登入成功後的核心戰情室程式碼
    # ==========================================
    name = st.session_state["name"]
    username = st.session_state["username"]
    
    user_role = config["credentials"]["usernames"][username]["role"]

    with st.sidebar:
        st.success(f"登入身分：{name} ({user_role})")
        authenticator.logout("安全登出系統", "sidebar", key="unique_logout_btn_123")
        st.markdown("---")

    st.title("✈️ 航空公司營運戰情室 ")
    st.markdown("整合 **六級風險診斷**、**多維限制最佳化**、**財務衝擊預測**、**動態航線風險 (Live)** 與 **AI 戰略幕僚** 的決策支援系統。")

    st.sidebar.header("📅 營運指標數據輸入")

    if user_role == "Commander":
        st.sidebar.subheader("【本年度 (Current Year)】")
        curr_safety = st.sidebar.slider("1. 飛安控管 (今年)", 0.0, 100.0, 75.0, step=1.0)
        curr_maint = st.sidebar.slider("2. 機隊維修 (今年)", 0.0, 100.0, 45.0, step=1.0)
        curr_otp = st.sidebar.slider("3. 航班調度 (今年)", 0.0, 100.0, 85.0, step=1.0)
        curr_service = st.sidebar.slider("4. 旅客服務 (今年)", 0.0, 100.0, 90.0, step=1.0)

        st.sidebar.divider()
        st.sidebar.subheader("【前年度 (Last Year)】")
        prev_safety = st.sidebar.slider("1. 飛安控管 (去年)", 0.0, 100.0, 85.0, step=1.0)
        prev_maint = st.sidebar.slider("2. 機隊維修 (去年)", 0.0, 100.0, 60.0, step=1.0)
        prev_otp = st.sidebar.slider("3. 航班調度 (去年)", 0.0, 100.0, 80.0, step=1.0)
        prev_service = st.sidebar.slider("4. 旅客服務 (去年)", 0.0, 100.0, 95.0, step=1.0)

        st.sidebar.divider()
        st.sidebar.subheader("🚧 系統資源限制 (Constraints)")
        total_budget = st.sidebar.number_input("💰 可用總預算 (百萬台幣)", min_value=10.0, value=500.0, step=10.0)
        max_labor_hours = st.sidebar.number_input("👷 最大可用維修工時 (小時)", min_value=1000, value=15000, step=500)
    else:
        st.sidebar.info("權限限制：您目前為「分析官」，僅具備檢視權限，無權進行最佳化資源重分配。")
        curr_safety, curr_maint, curr_otp, curr_service = 75.0, 45.0, 85.0, 90.0
        prev_safety, prev_maint, prev_otp, prev_service = 85.0, 60.0, 80.0, 95.0
        total_budget, max_labor_hours = 500.0, 15000

    categories = ['飛安控管', '機隊維修', '航班調度', '旅客服務']
    weights = np.array([0.40, 0.30, 0.20, 0.10])
    curr_scores = np.array([curr_safety, curr_maint, curr_otp, curr_service])
    prev_scores = np.array([prev_safety, prev_maint, prev_otp, prev_service])

    def objective(x, current_scores, weights):
        k_factors = np.array([1.5, 2.0, 1.2, 1.0])
        new_scores = np.clip(current_scores + k_factors * np.sqrt(x), 0, 100)
        return np.sum(weights * (100 - new_scores))

    con_budget = {'type': 'eq', 'fun': lambda x: np.sum(x) - total_budget}
    labor_req = np.array([20, 80, 10, 5])
    con_labor = {'type': 'ineq', 'fun': lambda x: max_labor_hours - np.sum(x * labor_req)}

    bounds = tuple((total_budget * 0.02, total_budget) for _ in range(4))
    initial_guess = np.array([total_budget/4]*4)

    result = minimize(objective, initial_guess, args=(curr_scores, weights), method='SLSQP', bounds=bounds, constraints=[con_budget, con_labor])
    allocations = result.x if result.success else initial_guess
    alloc_dict = {cat: alloc for cat, alloc in zip(categories, allocations)}

    def get_risk_level_config(score):
        if score == 100.0: return ('perfect', "#00d26a", "🏆 卓越典範 (PERFECT) —— 系統處於理想狀態，維持卓越並分享經驗")
        elif score >= 81.0: return ('stable', "#28a745", "✅ 安全穩定 (STABLE) —— 績效優良，持續精益求精與深化文化")
        elif score >= 61.0: return ('caution', "#ffc107", "⚠️ 黃色警戒 (CAUTION) —— 績效輕微下滑，需啟動主動式數據監測")
        elif score >= 41.0: return ('serious', "#fd7e14", "🟠 橘色風險 (SERIOUS) —— 存在組織性漏洞，需深度重整與系統性對策")
        elif score >= 21.0: return ('high_risk', "#e74c3c", "🔴 紅色高危 (HIGH RISK) —— 系統防禦失效，需立即介入與危機處置")
        else: return ('catastrophic', "#ff3333", "🚨 災難崩潰 (CATASTROPHIC) —— 組織機能癱瘓，立即停止營運並全面重審")

    def render_diagnosis_card(category, score, delta):
        level, main_color, status_text = get_risk_level_config(score)
        if delta >= 10: trend_label = f"📈 跨越式進步 (+{delta:.1f})"
        elif delta > 0: trend_label = f"↗️ 微幅進步 (+{delta:.1f})"
        elif delta <= -10: trend_label = f"📉 潰雪式衰退 ({delta:.1f})"
        elif delta < 0: trend_label = f"↘️ 微幅下滑 ({delta:.1f})"
        else: trend_label = "➖ 表現持平"

        st.markdown(f"""
        <div style="background-color: transparent; padding:20px; border-radius:10px; border: 1px solid {main_color}50; border-left: 8px solid {main_color}; margin-top: 20px; margin-bottom: 15px;">
            <h3 style="color: var(--text-color); margin-top:0;">
                {category} | 本年得分：<span style="color:{main_color}; font-size: 1.3em; font-weight: 900;">{score:.1f}</span> 
                <span style="font-size: 0.65em; font-weight: normal; opacity: 0.8;">({trend_label})</span>
            </h3>
            <p style="color: var(--text-color); font-weight:bold; font-size: 1.1em; margin-bottom:0;">判定：<span style="color:{main_color};">{status_text}</span></p>
        </div>
        """, unsafe_allow_html=True)
        return level

    knowledge_base = {
        '飛安控管': {
            'catastrophic': { 'reasons': ["安全管理系統 (SMS) 徹底癱瘓，內部甚至出現刻意隱瞞違規之現象。", "組織失去對風險的任何感知能力，隨時可能發生重大空難。"], 'actions': ["🚨 **[立即指令]** 總經理下令全機隊立即停飛，所有簽派與飛航作業強制暫停，等待外部聯合專案組進駐稽核。", "🚨 **[組織重整]** 解散現有安委會，凍結相關主管職權，重新考核核心關鍵崗位人員之飛安意識。"] },
            'high_risk': { 'reasons': ["防禦機制出現多重失效，「瑞士起司理論」漏洞穿透組織各層級。", "基層對「公正文化」完全失去信任，自願通報機制斷絕。"], 'actions': ["⚠️ **[危機處置]** 暫停高風險/易受天候影響航線運行，啟動無預警全機隊安全停飛檢查 (Stand-down)。", "⚠️ **[系統重審]** 全面盤點 SMS 運作狀況，重新驗證飛行員執照考勤與疲勞管理 (FRMS) 指標是否失真。"] },
            'serious': { 'reasons': ["存在組織性「孤島效應」，機務、航務與簽派數據無法有效橫向整合。", "SMS 退化為被動式的「事後檢討機制」，缺乏主動預測能力。"], 'actions': ["**[深度對策]** 成立總經理直屬專案小組，強制打通跨部門飛航數據壁壘。", "**[風險危害]** 針對輕微異常事件 (Incidents) 進行根本原因分析 (RCA)，找出組織層級的系統性漏洞。"] },
            'caution': { 'reasons': ["飛行員面臨潛在的疲勞累積，情境警覺 (Situational Awareness) 開始下滑。", "組員資源管理 (CRM) 訓練成效降低，駕駛艙內質疑權威能力轉弱。"], 'actions': ["**[主動監控]** 擴大 FOQA 飛行數據監測之分析深度，設定重落地、超速等偏差行為之嚴格警報門檻。", "**[組員資源]** 針對全體機師辦理「CRM 高階複訓」，強化面對複雜情境下的溝通效率與共同決策能力。"] },
            'stable': { 'reasons': ["防禦機制運作良好，數據監控與人員訓練均達標。"], 'actions': ["**[精益求精]** 系統運作穩健。請鼓勵公正文化 (Just Culture) 自願通報，找出隱藏在優良數據下的微小偏差。"] },
            'perfect': { 'reasons': ["已建立世界級飛安範本。組織上下視飛安為最高信仰。"], 'actions': ["**[卓越維持]** 策劃高強度、無預警的「重大空難場景模擬演習」，壓力測試組織之極端應變肌肉記憶。"] }
        },
        '機隊維修': {
            'catastrophic': { 'reasons': ["為趕工而選擇性忽略標準作業程序 (SOP)，甚至出現零件偽造或私自替代之嚴重違法行為。", "維修量能嚴重癱瘓，缺乏任何適航保障。"], 'actions': ["🚨 **[立即指令]** 總經理下令暫停所有非緊急維修作業，全面凍結現有機材庫存調度。", "🚨 **[全面重審]** 撤換維修廠長與品管主管，並將所有疑似違規之維修紀錄移送民航主管機關與司法單位調查。"] },
            'high_risk': { 'reasons': ["關鍵航材發生系統性斷鏈，導致機隊長期處於「缺件待料 (AOG)」導致安全裕度降低。", "維修排程失控導致嚴重「人為因素 (Human Factors)」失誤激增。"], 'actions': ["⚠️ **[危機處置]** 針對妥善率極差機型強制執行深度適航指令 (AD) 檢查，風險排除前無限期停飛。", "⚠️ **[流程整頓]** 嚴格取締任何形式的『捷徑行為 (Workarounds)』，應用預算立即採購備用發動機與耗材重建安全庫存。"] },
            'serious': { 'reasons': ["維修廠區溝通瑕疵嚴重，早晚班交接時發生嚴重資訊遺漏。", "維修數據流於紙本，缺乏可追溯性與預測能力。"], 'actions': ["**[深度對策]** 加速淘汰紙本工單，落實數位化維修記錄，確保每一個螺絲的更換都有數位簽章可循。", "**[供應鏈]** 重新評估零件供應鏈斷鏈風險，導入多元採購策略優化備料週期。"] },
            'caution': { 'reasons': ["第一線人員的人為因素 (Human Factors) 管理鬆動。", "老舊機型非預期故障率呈現上升趨勢。"], 'actions': ["**[強化防護]** 縮短發動機與關鍵航電設備的預防性更換週期。", "**[工廠管理]** 強制落實工具清點與雙重檢查 (Dual Inspection)，防範維修遺留物風險。"] },
            'stable': { 'reasons': ["妥善率維持在高檔，供應鏈健康。"], 'actions': ["**[精益求精]** 落實各機隊之例行 A、B、C、D 檢。", "**[數據轉型]** 開始利用感測器數據建立「AI 預測性維修 (Predictive Maintenance)」模型。"] },
            'perfect': { 'reasons': ["零維修事故紀錄。建立世界級機隊妥善率範本。"], 'actions': ["**[卓越維持]** 向業界分享「零失誤維修 (Zero-defect Maintenance)」管理經驗，並導入下一代更環保之維修技術。"] }
        },
        '航班調度': {
            'catastrophic': { 'reasons': ["時刻表與真實運能量嚴重錯配，造成大規模延誤與機組員嚴重超時。", "調度機能癱瘓，缺乏任何抗壓性。"], 'actions': ["🚨 **[立即指令]** 總經理下令強制取消該部門自行編排之所有航班時刻表，改用最低運能保障版時刻表。", "🚨 **[重大調整]** 徹換該部門核心管理團隊，並全面盤點組員疲勞與機隊妥善率缺口，策略性縮減營運網。"] },
            'high_risk': { 'reasons': ["時刻表毫無緩衝裕度 (Buffer Time)，雷雨季時缺乏因應手段導致航網崩潰。", "未科學計算備用機 (Spare Aircraft) 與待命組員 (Standby) 指派基數。"], 'actions': ["⚠️ **[危機處置]** 立即砍減延誤率常態性超過 40% 的『紙上航班』。", "⚠️ **[資源補足]** 動用緊急預算召回休假人員並應用數據模型重新精算備用機配置，在重點機場增加待命量能。"] },
            'serious': { 'reasons': ["簽派、機務與地勤之間的資訊傳遞存在嚴重時間差。", "缺乏突發事件的動態調度靈活度。"], 'actions': ["**[深度對策]** 重新繪製地停作業的甘特圖，精算並壓縮關鍵路徑 (Critical Path) 上的閒置時間。", "**[協同決策]** 建立 A-CDM (機場協同決策) 數據連線，提前預判流量管制。"] },
            'caution': { 'reasons': ["地停作業效率不彰，未能緊密銜接。"], 'actions': ["**[效率優化]** 重新優化飛機地停轉場流程（加油、上餐、清潔），並針對特定長程航班進行飛行計畫的燃油經濟性最佳化。"] },
            'stable': { 'reasons': ["準點率良好，抗壓性佳。"], 'actions': ["**[精益求精]** 維持高準點率紀錄，並試圖優化飛行路線降低燃油消耗。"] },
            'perfect': { 'reasons': ["達成年度零延誤紀錄（除天候因素）。建立世界級調度範本。"], 'actions': ["**[卓越維持]** 維持卓越營運，並將資源投入至提升機組員滿意度與長遠航網佈局。"] }
        },
        '旅客服務': {
            'catastrophic': { 'reasons': ["外包地勤或餐飲商履約品質極差，組織對其毫無控管能力。", "品牌形像災難性崩潰，旅客服務完全癱瘓。"], 'actions': ["🚨 **[立即指令]** 總經理下令暫停所有第三方代理商之履約作業，改由總部專案組直接介入。", "🚨 **[重大調整]** 開啟為期一個月的全面服務流程 BPR，並重新招標所有第三方代理商。"] },
            'high_risk': { 'reasons': ["第一線人員對異動航班 (IRROPS) 的處理 SOP 充滿模糊，旅客面對資訊黑洞。", "社群網路上出現大規模負面評價。"], 'actions': ["⚠️ **[危機處置]** 針對負評炸鍋服務斷點啟動緊急服務補救專案 (Service Recovery)。", "⚠️ **[流程重整]** 重新修訂異常航班處理補償標準，大幅下放前線主管權限，降低旅客憤怒感。"] },
            'serious': { 'reasons': ["數位化落後，APP在航班大亂時無法乘載流量且推播通知慢半拍。", "基層面對不理性旅客時，缺乏足夠的危機溝通訓練。"], 'actions': ["**[深度對策]** 強制升級 APP 伺服器並建立根本原因分析 (Root Cause Analysis)，找出導致不滿的核心關鍵字。"] },
            'caution': { 'reasons': ["外站各航點服務品質不一。"], 'actions': ["**[強化訓練]** 增加地勤與空服人員針對『奧客衝突與安撫』的實境模擬訓練，增強前線應變能力。"] },
            'stable': { 'reasons': ["服務品質穩定。"], 'actions': ["**[精益求精]** 定期進行神秘客 (Mystery Shopper) 抽查，確保品質一致。"] },
            'perfect': { 'reasons': ["達成年度零客訴紀錄。建立世界級服務範本。"], 'actions': ["**[卓越維持]** 向全體服務團隊發放卓越獎金，並投入個人化常客忠誠度計畫。"] }
        }
    }

    # ==========================================
    # 🌟 報表匯出功能
    # ==========================================
    report_content = f"""# 航空公司年度營運診斷與資源最佳化報告
    **報告生成時間：** {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    **總可用預算：** {total_budget} 百萬台幣 | **可用工時：** {max_labor_hours} 小時

    ## 一、 最佳化預算配置建議\n"""
    for cat, alloc in alloc_dict.items():
        report_content += f"- **{cat}**：建議投入 {alloc:.1f} 百萬台幣\n"

    report_content += "\n## 二、 深度專家診斷與改善行動方案\n"
    for i, cat in enumerate(categories):
        level, _, status_text = get_risk_level_config(curr_scores[i])
        data = knowledge_base[cat][level]
        report_content += f"\n### 【{cat}】 狀態判定：{status_text}\n"
        if level in ['catastrophic', 'high_risk', 'serious', 'caution']:
            report_content += "**🔍 潛在根本原因：**\n"
            for reason in data['reasons']:
                report_content += f"- {reason}\n"
        report_content += "**🛠️ 具體執行方案：**\n"
        for action in data['actions']:
            report_content += f"- {action}\n"

    st.sidebar.divider()
    st.sidebar.download_button(label="📄 匯出完整營運診斷書 (Report)", data=report_content, file_name="Airline_Operations_Report.md", mime="text/markdown")


    # ==========================================
    # API 函數定義 (氣象與軍事情報)
    # ==========================================
    @st.cache_data(show_spinner=False)
    def get_lat_lon(location_name):
        preset_coords = {
            "TPE (台北 桃園機場)": (25.0777, 121.2328),
            "NRT (東京 成田機場)": (35.7647, 140.3863),
            "SIN (新加坡 樟宜機場)": (1.3502, 103.9940),
            "FRA (法蘭克福機場)": (50.0333, 8.5705),
            "LHR (倫敦 希斯洛機場)": (51.4700, -0.4543),
            "JFK (紐約 甘迺迪機場)": (40.6413, -73.7781),
            "LAX (洛杉磯機場)": (33.9416, -118.4085),
            "DXB (杜拜機場)": (25.2532, 55.3657),
            "SYD (雪梨機場)": (-33.9461, 151.1772)
        }
        
        if location_name in preset_coords:
            return preset_coords[location_name]
            
        try:
            search_query = location_name.split('(')[0].strip() if '(' in location_name else location_name
            geolocator = Nominatim(user_agent="airline_dashboard_v7")
            loc = geolocator.geocode(search_query, timeout=10)
            if loc: return loc.latitude, loc.longitude
            return None, None
        except: 
            return None, None

    @st.cache_data(ttl=600, show_spinner=False)
    def get_live_weather(lat, lon):
        try:
            url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,wind_speed_10m,weather_code&wind_speed_unit=kn"
            res = requests.get(url, timeout=5).json()
            curr = res.get('current', {})
            wind_kt = curr.get('wind_speed_10m', "N/A")
            temp_c = curr.get('temperature_2m', "N/A")
            
            code = curr.get('weather_code', 0)
            if code in [0, 1, 2, 3]: condition = "晴朗/多雲 🌤️"
            elif code in [45, 48]: condition = "濃霧視障 🌫️"
            elif code in [51, 53, 55, 61, 63, 65, 80, 81, 82]: condition = "降雨/陣雨 🌧️"
            elif code in [71, 73, 75, 77, 85, 86]: condition = "降雪 ❄️"
            elif code in [95, 96, 99]: condition = "雷暴/極端不穩定 ⛈️"
            else: condition = "未知氣候"
                
            return wind_kt, temp_c, condition
        except:
            return "N/A", "N/A", "連線失敗"

    @st.cache_data(ttl=600, show_spinner=False)
    def get_global_conflict_alerts():
        try:
            # 🌟 升級版：切換為 Google News 繁體中文軍事警戒網
            url = "https://news.google.com/rss/search?q=飛彈+OR+空襲+OR+軍事衝突+OR+開戰+OR+防空&hl=zh-TW&gl=TW&ceid=TW:zh-Hant"
            feed = feedparser.parse(url)
            
            alerts = []
            for entry in feed.entries[:3]: # 直接抓取最新 3 筆重大警戒
                # 清除標題後綴的新聞來源名稱，保持版面乾淨
                clean_title = entry.title.rsplit(' - ', 1)[0]
                pub_date = entry.published if 'published' in entry else ""
                alerts.append({
                    "title": clean_title,
                    "date": pub_date,
                    "link": entry.link
                })
            return alerts
        except:
            return []

    # ==========================================
    # 建立五大頁籤架構
    # ==========================================
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 核心診斷分配", "📈 長期趨勢", "💸 財務沙盤推演", "🌍 全球航線風險評估", "🤖 AI 戰略幕僚"])

    with tab1:
        col1, col2 = st.columns([1.2, 1])
        with col1:
            st.subheader("🔄 年度營運體質對比雷達圖")
            fig = go.Figure()
            fig.add_trace(go.Scatterpolar(r=[100]*5, theta=categories+[categories[0]], fill=None, name='目標標準', line=dict(color='mediumseagreen', dash='dash')))
            fig.add_trace(go.Scatterpolar(r=list(prev_scores)+[prev_scores[0]], theta=categories+[categories[0]], fill='toself', name='前年度', line_color='rgba(150, 150, 150, 0.5)'))
            fig.add_trace(go.Scatterpolar(r=list(curr_scores)+[curr_scores[0]], theta=categories+[categories[0]], fill='toself', name='本年度', line_color='royalblue', fillcolor='rgba(65, 105, 225, 0.2)'))
            fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), margin=dict(l=40, r=40, t=30, b=30))
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("📈 年度指標與最佳化分配 (YOY)")
            st.caption("✅ 系統已自動平衡「預算上限」與「維修工時」雙重限制。")
            m_cols = st.columns(2)
            for i, cat in enumerate(categories):
                delta = curr_scores[i] - prev_scores[i]
                with m_cols[i % 2]:
                    st.metric(label=cat, value=f"{curr_scores[i]:.1f}", delta=f"{delta:.1f}")
                    st.caption(f"💰 建議預算: **{alloc_dict[cat]:.1f} 百萬**")

        st.divider()
        st.subheader("📋 年度趨勢診斷報告與具體改善行動書")
        for i, cat in enumerate(categories):
            delta = curr_scores[i] - prev_scores[i]
            level = render_diagnosis_card(cat, curr_scores[i], delta)
            data = knowledge_base[cat][level]
            
            expanded = level not in ['perfect', 'stable']
            with st.expander(f"🔍 查看深度診斷分析報告...", expanded=expanded):
                if level in ['catastrophic', 'high_risk', 'serious', 'caution']:
                    st.markdown(f"#### 🔍 潛在根本原因 (Root Cause)")
                    for reason in data['reasons']: st.markdown(f"- 🚩 {reason}")
                    st.markdown("---")
                
                st.markdown(f"#### 🛠️ 具體執行方案 (Action Plan)")
                for action in data['actions']: st.markdown(f"- {action}")
                st.markdown("<br>", unsafe_allow_html=True)

    with tab2:
        st.subheader("📈 歷史營運數據趨勢分析 (五年期)")
        st.markdown("您可以上傳包含歷史數據的 CSV 檔案，或查看系統預設的模擬數據。")
        uploaded_file = st.file_uploader("📂 上傳歷史營運數據 (CSV)", type="csv")
        
        if uploaded_file is not None:
            df_trend = pd.read_csv(uploaded_file)
            st.success("檔案讀取成功！")
        else:
            years = ['2022', '2023', '2024', '2025', '2026(YTD)']
            df_trend = pd.DataFrame({'年份': years, '飛安控管': [92, 88, 85, prev_safety, curr_safety], '機隊維修': [80, 75, 65, prev_maint, curr_maint], '航班調度': [88, 85, 82, prev_otp, curr_otp], '旅客服務': [85, 90, 92, prev_service, curr_service]})
        
        df_melted = df_trend.melt(id_vars=['年份'], var_name='營運指標', value_name='分數')
        fig_line = px.line(df_melted, x='年份', y='分數', color='營運指標', markers=True, title='各項營運指標長期趨勢追蹤')
        fig_line.update_layout(yaxis=dict(range=[0, 100]))
        st.plotly_chart(fig_line, use_container_width=True)
        
        with st.expander("📄 查看詳細數據表格"):
            st.dataframe(df_trend, use_container_width=True)

    with tab3:
        st.subheader("💸 財務沙盤推演 (ROI Simulator)")
        st.markdown("將「營運分數缺口」換算為真實營業損失預估，並手動調配預算測試投資報酬率。")
        st.info(f"您目前共有 **{total_budget} 百萬** 的籌碼可以分配。")
        
        sim_cols = st.columns(4)
        sim_allocs = []
        for i, cat in enumerate(categories):
            with sim_cols[i]:
                val = st.number_input(f"投入【{cat}】(百萬)", min_value=0.0, max_value=float(total_budget), value=float(alloc_dict[cat]), step=10.0, key=f"sim_{i}")
                sim_allocs.append(val)
                
        total_sim = sum(sim_allocs)
        if total_sim > total_budget:
            st.error(f"⚠️ 預算超支！您分配了 {total_sim} 百萬，但總預算只有 {total_budget} 百萬。")
        else:
            k_factors = np.array([1.5, 2.0, 1.2, 1.0])
            predicted_scores = np.clip(curr_scores + k_factors * np.sqrt(sim_allocs), 0, 100)
            
            loss_factors = [2.5, 3.0, 1.8, 0.5]
            current_loss = np.sum((100 - curr_scores) * loss_factors)
            predicted_loss = np.sum((100 - predicted_scores) * loss_factors)
            saved_money = current_loss - predicted_loss
            
            st.success(f"✅ 模擬完成！可為公司 **減少 {saved_money:.1f} 百萬隱性損失**。")
            
            fig_sim = go.Figure()
            fig_sim.add_trace(go.Scatterpolar(r=[100]*5, theta=categories+[categories[0]], fill=None, name='目標標準', line=dict(color='mediumseagreen', dash='dash')))
            fig_sim.add_trace(go.Scatterpolar(r=list(curr_scores)+[curr_scores[0]], theta=categories+[categories[0]], fill='toself', name='本年度現況', line_color='rgba(150, 150, 150, 0.5)'))
            fig_sim.add_trace(go.Scatterpolar(r=list(predicted_scores)+[predicted_scores[0]], theta=categories+[categories[0]], fill='toself', name='明年度預測', line_color='mediumseagreen', fillcolor='rgba(46, 204, 113, 0.3)'))
            fig_sim.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), margin=dict(l=40, r=40, t=30, b=30))
            
            loss_cols = st.columns([1.2, 1])
            with loss_cols[0]:
                st.plotly_chart(fig_sim, use_container_width=True)
            with loss_cols[1]:
                st.write("### 📉 投資報酬率分析")
                st.metric("🔴 目前預估年度隱性損失", f"{current_loss:.1f} 百萬", "維持現狀的代價", delta_color="inverse")
                st.metric("🟢 模擬後預估年度隱性損失", f"{predicted_loss:.1f} 百萬", f"投資報酬率 (ROI): {((saved_money/total_sim)*100):.1f}%" if total_sim>0 else "0%", delta_color="normal")

    with tab4:
        st.subheader("🌍 全球動態航線風險評估 (Live API 串接版)")
        st.markdown("系統已成功串接 **Geocoding API**, **Open-Meteo**, **OpenSky** 與 **RSS 全球軍事警戒網**。")
        
        airport_presets = [
            "TPE (台北 桃園機場)", "NRT (東京 成田機場)", "SIN (新加坡 樟宜機場)",
            "FRA (法蘭克福機場)", "LHR (倫敦 希斯洛機場)", "JFK (紐約 甘迺迪機場)",
            "LAX (洛杉磯機場)", "DXB (杜拜機場)", "SYD (雪梨機場)", "🌍 自行輸入其他地點..."
        ]

        route_col1, route_col2 = st.columns(2)
        with route_col1:
            origin_sel = st.selectbox("🛫 選擇起飛機場 (Origin)", airport_presets, index=0)
            if origin_sel == "🌍 自行輸入其他地點...":
                origin_input = st.text_input("請輸入起飛地點 (中英文皆可)：", placeholder="例如: 巴黎, 曼谷 BKK...")
            else:
                origin_input = origin_sel

        with route_col2:
            dest_sel = st.selectbox("🛬 選擇降落機場 (Destination)", airport_presets, index=3)
            if dest_sel == "🌍 自行輸入其他地點...":
                dest_input = st.text_input("請輸入降落地點 (中英文皆可)：", placeholder="例如: 羅馬, 首爾 ICN...")
            else:
                dest_input = dest_sel

        if origin_input and dest_input:
            with st.spinner('📡 正在透過全球衛星系統定位座標並抓取情報中...'):
                o_lat, o_lon = get_lat_lon(origin_input)
                d_lat, d_lon = get_lat_lon(dest_input)

            if o_lat is None:
                st.error(f"❌ 找不到起飛地點「{origin_input}」的座標。")
            elif d_lat is None:
                st.error(f"❌ 找不到降落地點「{dest_input}」的座標。")
            elif o_lat == d_lat and o_lon == d_lon:
                st.warning("⚠️ 起飛與降落地點過於接近或相同，無法計算航線。")
            else:
                mid_lat = (o_lat + d_lat) / 2
                mid_lon = (o_lon + d_lon) / 2
                
                o_wind, o_temp, o_cond = get_live_weather(o_lat, o_lon)
                d_wind, d_temp, d_cond = get_live_weather(d_lat, d_lon)
                mid_wind, mid_temp, mid_cond = get_live_weather(mid_lat, mid_lon)

                try:
                    bbox = f"lamin={mid_lat-5}&lomin={mid_lon-5}&lamax={mid_lat+5}&lomax={mid_lon+5}"
                    air_res = requests.get(f"https://opensky-network.org/api/states/all?{bbox}", timeout=3).json()
                    flights = air_res['states'] if air_res and 'states' in air_res else []
                    f_lats = [f[6] for f in flights[:50] if f[6]]
                    f_lons = [f[5] for f in flights[:50] if f[5]]
                    traffic_status = "🟢 成功接入 OpenSky 真實即時航班雷達"
                except:
                    f_lats = mid_lat + np.random.uniform(-8, 8, 30)
                    f_lons = mid_lon + np.random.uniform(-8, 8, 30)
                    traffic_status = "🟡 OpenSky 伺服器忙碌，切換為智慧模擬航班流量"

                detour_lat = max(min(mid_lat - 15, 89.0), -89.0)
                detour_lon = mid_lon + 15
                if detour_lon > 180: detour_lon -= 360
                elif detour_lon < -180: detour_lon += 360

                fig_map = go.Figure()

                fig_map.add_trace(go.Scattergeo(
                    lat=[mid_lat], lon=[mid_lon],
                    marker=dict(size=120, color='red', opacity=0.2),
                    name="🚨 模擬戰區", mode="markers"
                ))

                fig_map.add_trace(go.Scattergeo(
                    lat=[o_lat, mid_lat, d_lat], lon=[o_lon, mid_lon, d_lon],
                    mode='lines+markers', line=dict(width=3, color='red', dash='dash'),
                    name="原訂直飛航線 (高風險)", text=[origin_input[:5], "Danger Zone", dest_input[:5]], textposition="bottom center"
                ))

                fig_map.add_trace(go.Scattergeo(
                    lat=[o_lat, detour_lat, d_lat], lon=[o_lon, detour_lon, d_lon],
                    mode='lines+markers', line=dict(width=3, color='mediumseagreen'),
                    name="建議備用航線 (安全繞飛)", text=[origin_input[:5], "Safe Waypoint", dest_input[:5]], textposition="bottom center"
                ))

                if len(f_lats) > 0:
                    fig_map.add_trace(go.Scattergeo(
                        lat=f_lats, lon=f_lons,
                        mode='markers', marker=dict(symbol='circle', size=6, color='yellow', line=dict(width=1, color='black')),
                        name="✈️ 周邊民航機即時動態"
                    ))

                fig_map.update_geos(
                    projection_type="natural earth",
                    showcountries=True, countrycolor="RebeccaPurple",
                    showland=True, landcolor="rgb(30, 30, 30)", oceancolor="rgb(10, 10, 20)", showocean=True,
                    lataxis_range=[min(o_lat, d_lat, detour_lat)-20, max(o_lat, d_lat, detour_lat)+20], 
                    lonaxis_range=[min(o_lon, d_lon, detour_lon)-20, max(o_lon, d_lon, detour_lon)+20]
                )
                fig_map.update_layout(height=500, margin=dict(l=0, r=0, t=30, b=0), paper_bgcolor="rgb(10, 10, 10)", legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01))
                st.caption(traffic_status)
                st.plotly_chart(fig_map, use_container_width=True)

                st.markdown("### 🌤️ 即時飛航氣象簡報 (Live METAR/Weather)")
                w_col1, w_col2, w_col3 = st.columns(3)
                with w_col1:
                    st.info(f"**🛫 起飛地：{origin_input[:10]}**\n\n- 氣候狀態：{o_cond}\n- 實時氣溫：{o_temp} °C\n- 地表風速：{o_wind} 節 (kt)")
                with w_col2:
                    st.warning(f"**⚠️ 航路中繼：危險管制區**\n\n- 氣候狀態：{mid_cond}\n- 實時氣溫：{mid_temp} °C\n- 航路風速：{mid_wind} 節 (kt)")
                with w_col3:
                    st.success(f"**🛬 降落地：{dest_input[:10]}**\n\n- 氣候狀態：{d_cond}\n- 實時氣溫：{d_temp} °C\n- 地表風速：{d_wind} 節 (kt)")

                st.divider()

                map_col1, map_col2 = st.columns(2)
                with map_col1:
                    st.error(f"### 🚨 全球軍事與地緣政治警戒 (LIVE)")
                    
                    live_alerts = get_global_conflict_alerts()
                    if live_alerts:
                        st.markdown("**📡 戰情室即時攔截情報：**")
                        for idx, alert in enumerate(live_alerts):
                            # 🌟 升級版：支援自動明暗模式切換的透明護眼排版，字體保證清晰！
                            st.markdown(f"""
                            <div style='background-color: rgba(255, 75, 75, 0.1); padding:10px; border-left:4px solid #ff4b4b; margin-bottom:10px; border-radius:5px;'>
                                <strong style='color:#ff4b4b;'>[威脅情報 {idx+1}]</strong> <span style='color: var(--text-color); font-weight: bold;'>{alert['title']}</span><br>
                                <span style='font-size:0.8em; color: gray;'>發布時間: {alert['date']}</span>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.success("✅ 當前全球監測網未攔截到重大軍事或飛彈衝突情報。")
                        
                    st.markdown("---")    
                    st.button("❌ 拒絕此航線並發布避讓指令", type="primary")

                with map_col2:
                    st.success("### ✅ 系統建議：啟用動態安全繞道航線")
                    st.markdown("""
                    **改道路徑：** 系統已自動計算偏置航路避開高風險管制區，防止潛在的系統性失效點對齊。
                    - **🛡️ 飛安評估：** 避開交戰與干擾熱區，導航訊號穩定。
                    """)
                    
                    rough_dist = np.sqrt((o_lat-d_lat)**2 + (o_lon-d_lon)**2)
                    delay_mins = int(rough_dist * 1.5 + np.random.randint(20, 45))
                    fuel_tons = round(delay_mins * 0.15, 1)

                    st.markdown("#### 💰 繞道營運成本評估 (Delta Cost)")
                    c1, c2, c3 = st.columns(3)
                    c1.metric("增加飛行時間", f"+ {delay_mins} 分鐘", delta_color="inverse")
                    c2.metric("額外燃油消耗", f"+ {fuel_tons} 噸", delta_color="inverse")
                    c3.metric("航班準點率影響", "延遲抵達", delta_color="inverse")
                    
                    st.button("✅ 批准並重新簽派 (Approve & Dispatch)")

    with tab5:
        st.subheader("🤖 AI 戰略幕僚 (Virtual Advisor)")
        st.info(f"🧠 **系統 Context 已同步**：內外部數據 (營運體質、航線氣象、即時軍事警戒) 皆已連線。")
        
        try:
            api_key = st.secrets.get("OPENAI_API_KEY", "")
        except:
            api_key = ""
            st.error("⚠️ 系統找不到 API Key！請確定您已經將密碼設定在 Streamlit 的 Secrets 中。")
        
        uq = st.chat_input("請輸入戰略問題 (例：請綜合評估目前這條航線的地緣政治風險，並給予簽派建議)...")
        
        if uq:
            st.chat_message("user").write(uq)
            
            with st.chat_message("assistant"):
                if not api_key:
                    st.error("⚠️ 缺少 OpenAI API Key，無法啟動 AI 幕僚。")
                else:
                    with st.spinner("AI 幕僚正在交叉比對「內部營運數據」與「全球即時威脅雷達」..."):
                        try:
                            from openai import OpenAI
                            client = OpenAI(api_key=api_key)
                            
                            # 【安全擷取 Tab 4 的即時外部數據】避免網路錯誤時當機
                            route_str = f"{locals().get('origin_input', '未知')} 飛往 {locals().get('dest_input', '未知')}"
                            weather_str = f"起飛區({locals().get('o_cond', '未知')}, {locals().get('o_wind', '未知')}kt) -> 航路中繼({locals().get('mid_cond', '未知')}, {locals().get('mid_wind', '未知')}kt) -> 降落區({locals().get('d_cond', '未知')}, {locals().get('d_wind', '未知')}kt)"
                            
                            alerts = locals().get('live_alerts', [])
                            alert_str = "、".join([a['title'] for a in alerts]) if alerts else "目前全球監測網無重大軍事或飛彈衝突情報。"
                            
                            system_prompt = f"""
                            你是一位擁有20年經驗的"航空公司營運與飛航安全戰略幕僚"。
                            你的說話風格專業、自然、冷靜且具備同理心，就像一位真實存在的高階軍事/航空顧問。
                            
                            [嚴格限制與職責]
                            1. 領域限制：你的回答必須絕對限制在"航空營運、安全管理系統(SMS)、風險分析(如瑞士起司模型)、機隊維修、航線威脅評估、地緣政治飛安影響、飛彈危機應對"領域。若問題無關，請禮貌引導回飛安主題。
                            2. 數據支撐：請務必「融合」以下兩大板塊的即時數據來提供客製化建議：
                            
                               【板塊一：內部營運體質】
                               - 當前飛安控管評分：{curr_safety} / 100
                               - 當前機隊維修評分：{curr_maint} / 100
                               - 當前航班調度評分：{curr_otp} / 100
                               - 當前旅客服務評分：{curr_service} / 100
                               - 總經理可動用的總預算：{total_budget} 百萬台幣
                               - 剩餘可用的維修工時：{max_labor_hours} 小時
                               
                               【板塊二：外部動態航線威脅 (LIVE)】
                               - 當前監控航線：{route_str}
                               - 即時氣象威脅：{weather_str}
                               - 全球地緣軍事警戒：{alert_str}
                            """
                            
                            response = client.chat.completions.create(
                                model="gpt-4o-mini",
                                messages=[
                                    {"role": "system", "content": system_prompt},
                                    {"role": "user", "content": uq}
                                ],
                                temperature=0.7
                            )
                            
                            ai_reply = response.choices[0].message.content
                            st.write(ai_reply)
                            
                        except Exception as e:
                            st.error("⚠️ 啟動 AI 幕僚失敗。請確認網路連線或 API 額度狀況。")
                            st.caption(f"錯誤代碼: {e}")
                            st.caption(f"錯誤代碼: {e}")
