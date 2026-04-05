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
import urllib.parse 

from auth_system import setup_authenticator 

# ==========================================
# 0. 網頁基本設定 
# ==========================================
st.set_page_config(page_title="航空公司營運戰情室 (God Mode)", layout="wide", initial_sidebar_state="expanded")

# ==========================================
# 🔒 全局 API Key 讀取與 Session 記憶體初始化
# ==========================================
try:
    api_key = st.secrets.get("OPENAI_API_KEY", "")
except:
    api_key = ""

# AI 財務報告記憶體 (避免拉動滑桿時消失)
if "finance_ai_report" not in st.session_state:
    st.session_state["finance_ai_report"] = None
if "last_sim_inputs" not in st.session_state:
    st.session_state["last_sim_inputs"] = ""

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

    st.title("✈️ 航空公司營運戰情室 (Aviation War Room - 企業頂規版)")
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
        # 🌟 徹底解鎖預算天花板，預設千億台幣格局
        total_budget = st.sidebar.number_input(
            "💰 可用總預算 (百萬台幣)", 
            min_value=10.0, 
            max_value=None, 
            value=100000.0, 
            step=1000.0, 
            format="%.1f"
        )
        max_labor_hours = st.sidebar.number_input("👷 最大可用維修工時 (小時)", min_value=1000, value=15000, step=500)
    else:
        st.sidebar.info("權限限制：您目前為「分析官」，僅具備檢視權限，無權進行最佳化資源重分配。")
        curr_safety, curr_maint, curr_otp, curr_service = 75.0, 45.0, 85.0, 90.0
        prev_safety, prev_maint, prev_otp, prev_service = 85.0, 60.0, 80.0, 95.0
        total_budget, max_labor_hours = 100000.0, 15000

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
        if score == 100.0: return ('perfect', "#00d26a", "🏆 卓越典範 (PERFECT)")
        elif score >= 81.0: return ('stable', "#28a745", "✅ 安全穩定 (STABLE)")
        elif score >= 61.0: return ('caution', "#ffc107", "⚠️ 黃色警戒 (CAUTION)")
        elif score >= 41.0: return ('serious', "#fd7e14", "🟠 橘色風險 (SERIOUS)")
        elif score >= 21.0: return ('high_risk', "#e74c3c", "🔴 紅色高危 (HIGH RISK)")
        else: return ('catastrophic', "#ff3333", "🚨 災難崩潰 (CATASTROPHIC)")

    # ==========================================
    # 🌟 完整展開的深度知識庫 (拒絕壓縮，保持可讀性)
    # ==========================================
    knowledge_base = {
        '飛安控管': {
            'catastrophic': { 
                'reasons': ["安全管理系統 (SMS) 徹底癱瘓，內部甚至出現刻意隱瞞違規之現象。", "組織失去對風險的任何感知能力，隨時可能發生重大空難。"], 
                'actions': ["🚨 **[立即指令]** 總經理下令全機隊立即停飛，所有簽派與飛航作業強制暫停，等待外部聯合專案組進駐稽核。", "🚨 **[組織重整]** 解散現有安委會，凍結相關主管職權，重新考核核心關鍵崗位人員之飛安意識。"] 
            },
            'high_risk': { 
                'reasons': ["防禦機制出現多重失效，「瑞士起司理論」漏洞穿透組織各層級。", "基層對「公正文化」完全失去信任，自願通報機制斷絕。"], 
                'actions': ["⚠️ **[危機處置]** 暫停高風險/易受天候影響航線運行，啟動無預警全機隊安全停飛檢查 (Stand-down)。", "⚠️ **[系統重審]** 全面盤點 SMS 運作狀況，重新驗證飛行員執照考勤與疲勞管理 (FRMS) 指標是否失真。"] 
            },
            'serious': { 
                'reasons': ["存在組織性「孤島效應」，機務、航務與簽派數據無法有效橫向整合。", "SMS 退化為被動式的「事後檢討機制」，缺乏主動預測能力。"], 
                'actions': ["**[深度對策]** 成立總經理直屬專案小組，強制打通跨部門飛航數據壁壘。", "**[風險危害]** 針對輕微異常事件 (Incidents) 進行根本原因分析 (RCA)，找出組織層級的系統性漏洞。"] 
            },
            'caution': { 
                'reasons': ["飛行員面臨潛在的疲勞累積，情境警覺 (Situational Awareness) 開始下滑。", "組員資源管理 (CRM) 訓練成效降低，駕駛艙內質疑權威能力轉弱。"], 
                'actions': ["**[主動監控]** 擴大 FOQA 飛行數據監測之分析深度，設定重落地、超速等偏差行為之嚴格警報門檻。", "**[組員資源]** 針對全體機師辦理「CRM 高階複訓」，強化面對複雜情境下的溝通效率與共同決策能力。"] 
            },
            'stable': { 
                'reasons': ["防禦機制運作良好，數據監控與人員訓練均達標。"], 
                'actions': ["**[精益求精]** 系統運作穩健。請鼓勵公正文化 (Just Culture) 自願通報，找出隱藏在優良數據下的微小偏差。"] 
            },
            'perfect': { 
                'reasons': ["已建立世界級飛安範本。組織上下視飛安為最高信仰。"], 
                'actions': ["**[卓越維持]** 策劃高強度、無預警的「重大空難場景模擬演習」，壓力測試組織之極端應變肌肉記憶。"] 
            }
        },
        '機隊維修': {
            'catastrophic': { 
                'reasons': ["為趕工而選擇性忽略標準作業程序 (SOP)，甚至出現零件偽造或私自替代之嚴重違法行為。", "維修量能嚴重癱瘓，缺乏任何適航保障。"], 
                'actions': ["🚨 **[立即指令]** 總經理下令暫停所有非緊急維修作業，全面凍結現有機材庫存調度。", "🚨 **[全面重審]** 撤換維修廠長與品管主管，並將所有疑似違規之維修紀錄移送民航主管機關與司法單位調查。"] 
            },
            'high_risk': { 
                'reasons': ["關鍵航材發生系統性斷鏈，導致機隊長期處於「缺件待料 (AOG)」導致安全裕度降低。", "維修排程失控導致嚴重「人為因素 (Human Factors)」失誤激增。"], 
                'actions': ["⚠️ **[危機處置]** 針對妥善率極差機型強制執行深度適航指令 (AD) 檢查，風險排除前無限期停飛。", "⚠️ **[流程整頓]** 嚴格取締任何形式的『捷徑行為 (Workarounds)』，應用預算立即採購備用發動機與耗材重建安全庫存。"] 
            },
            'serious': { 
                'reasons': ["維修廠區溝通瑕疵嚴重，早晚班交接時發生嚴重資訊遺漏。", "維修數據流於紙本，缺乏可追溯性與預測能力。"], 
                'actions': ["**[深度對策]** 加速淘汰紙本工單，落實數位化維修記錄，確保每一個螺絲的更換都有數位簽章可循。", "**[供應鏈]** 重新評估零件供應鏈斷鏈風險，導入多元採購策略優化備料週期。"] 
            },
            'caution': { 
                'reasons': ["第一線人員的人為因素 (Human Factors) 管理鬆動。", "老舊機型非預期故障率呈現上升趨勢。"], 
                'actions': ["**[強化防護]** 縮短發動機與關鍵航電設備的預防性更換週期。", "**[工廠管理]** 強制落實工具清點與雙重檢查 (Dual Inspection)，防範維修遺留物風險。"] 
            },
            'stable': { 
                'reasons': ["妥善率維持在高檔，供應鏈健康。"], 
                'actions': ["**[精益求精]** 落實各機隊之例行 A、B、C、D 檢。", "**[數據轉型]** 開始利用感測器數據建立「AI 預測性維修 (Predictive Maintenance)」模型。"] 
            },
            'perfect': { 
                'reasons': ["零維修事故紀錄。建立世界級機隊妥善率範本。"], 
                'actions': ["**[卓越維持]** 向業界分享「零失誤維修 (Zero-defect Maintenance)」管理經驗，並導入下一代更環保之維修技術。"] 
            }
        },
        '航班調度': {
            'catastrophic': { 
                'reasons': ["時刻表與真實運能量嚴重錯配，造成大規模延誤與機組員嚴重超時。", "調度機能癱瘓，缺乏任何抗壓性。"], 
                'actions': ["🚨 **[立即指令]** 總經理下令強制取消該部門自行編排之所有航班時刻表，改用最低運能保障版時刻表。", "🚨 **[重大調整]** 徹換該部門核心管理團隊，並全面盤點組員疲勞與機隊妥善率缺口，策略性縮減營運網。"] 
            },
            'high_risk': { 
                'reasons': ["時刻表毫無緩衝裕度 (Buffer Time)，雷雨季時缺乏因應手段導致航網崩潰。", "未科學計算備用機 (Spare Aircraft) 與待命組員 (Standby) 指派基數。"], 
                'actions': ["⚠️ **[危機處置]** 立即砍減延誤率常態性超過 40% 的『紙上航班』。", "⚠️ **[資源補足]** 動用緊急預算召回休假人員並應用數據模型重新精算備用機配置，在重點機場增加待命量能。"] 
            },
            'serious': { 
                'reasons': ["簽派、機務與地勤之間的資訊傳遞存在嚴重時間差。", "缺乏突發事件的動態調度靈活度。"], 
                'actions': ["**[深度對策]** 重新繪製地停作業的甘特圖，精算並壓縮關鍵路徑 (Critical Path) 上的閒置時間。", "**[協同決策]** 建立 A-CDM (機場協同決策) 數據連線，提前預判流量管制。"] 
            },
            'caution': { 
                'reasons': ["地停作業效率不彰，未能緊密銜接。"], 
                'actions': ["**[效率優化]** 重新優化飛機地停轉場流程（加油、上餐、清潔），並針對特定長程航班進行飛行計畫的燃油經濟性最佳化。"] 
            },
            'stable': { 
                'reasons': ["準點率良好，抗壓性佳。"], 
                'actions': ["**[精益求精]** 維持高準點率紀錄，並試圖優化飛行路線降低燃油消耗。"] 
            },
            'perfect': { 
                'reasons': ["達成年度零延誤紀錄（除天候因素）。建立世界級調度範本。"], 
                'actions': ["**[卓越維持]** 維持卓越營運，並將資源投入至提升機組員滿意度與長遠航網佈局。"] 
            }
        },
        '旅客服務': {
            'catastrophic': { 
                'reasons': ["外包地勤或餐飲商履約品質極差，組織對其毫無控管能力。", "品牌形像災難性崩潰，旅客服務完全癱瘓。"], 
                'actions': ["🚨 **[立即指令]** 總經理下令暫停所有第三方代理商之履約作業，改由總部專案組直接介入。", "🚨 **[重大調整]** 開啟為期一個月的全面服務流程 BPR，並重新招標所有第三方代理商。"] 
            },
            'high_risk': { 
                'reasons': ["第一線人員對異動航班 (IRROPS) 的處理 SOP 充滿模糊，旅客面對資訊黑洞。", "社群網路上出現大規模負面評價。"], 
                'actions': ["⚠️ **[危機處置]** 針對負評炸鍋服務斷點啟動緊急服務補救專案 (Service Recovery)。", "⚠️ **[流程重整]** 重新修訂異常航班處理補償標準，大幅下放前線主管權限，降低旅客憤怒感。"] 
            },
            'serious': { 
                'reasons': ["數位化落後，APP在航班大亂時無法乘載流量且推播通知慢半拍。", "基層面對不理性旅客時，缺乏足夠的危機溝通訓練。"], 
                'actions': ["**[深度對策]** 強制升級 APP 伺服器並建立根本原因分析 (Root Cause Analysis)，找出導致不滿的核心關鍵字。"] 
            },
            'caution': { 
                'reasons': ["外站各航點服務品質不一。"], 
                'actions': ["**[強化訓練]** 增加地勤與空服人員針對『奧客衝突與安撫』的實境模擬訓練，增強前線應變能力。"] 
            },
            'stable': { 
                'reasons': ["服務品質穩定。"], 
                'actions': ["**[精益求精]** 定期進行神秘客 (Mystery Shopper) 抽查，確保品質一致。"] 
            },
            'perfect': { 
                'reasons': ["達成年度零客訴紀錄。建立世界級服務範本。"], 
                'actions': ["**[卓越維持]** 向全體服務團隊發放卓越獎金，並投入個人化常客忠誠度計畫。"] 
            }
        }
    }

    # ==========================================
    # 建立五大頁籤架構
    # ==========================================
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 核心診斷分配", "📈 長期趨勢", "💸 財務沙盤推演", "🌍 全球航線風險評估", "🤖 AI 戰略幕僚"])

    with tab1:
        st.subheader("📈 年度指標與最佳化分配 (YOY)")
        m_cols = st.columns(4)
        for i, cat in enumerate(categories):
            delta = curr_scores[i] - prev_scores[i]
            with m_cols[i]:
                st.metric(label=cat, value=f"{curr_scores[i]:.1f}", delta=f"{delta:.1f}")
                st.caption(f"💰 建議預算: {alloc_dict[cat]:.1f} M")
                
        st.divider()
        st.subheader("📋 年度趨勢診斷報告與具體改善行動書")
        for i, cat in enumerate(categories):
            level, main_color, status_text = get_risk_level_config(curr_scores[i])
            data = knowledge_base[cat][level]
            with st.expander(f"🔍 {cat} 診斷報告 ({status_text})", expanded=(level not in ['perfect', 'stable'])):
                st.markdown("**🚨 潛在根本原因：**")
                for reason in data['reasons']:
                    st.markdown(f"- {reason}")
                st.markdown("**🛠️ 具體執行方案：**")
                for action in data['actions']:
                    st.markdown(f"- {action}")

    with tab2:
        st.subheader("📈 歷史營運數據趨勢分析 (五年期)")
        years = ['2022', '2023', '2024', '2025', '2026(YTD)']
        df_trend = pd.DataFrame({'年份': years, '飛安控管': [92, 88, 85, prev_safety, curr_safety], '機隊維修': [80, 75, 65, prev_maint, curr_maint], '航班調度': [88, 85, 82, prev_otp, curr_otp], '旅客服務': [85, 90, 92, prev_service, curr_service]})
        df_melted = df_trend.melt(id_vars=['年份'], var_name='營運指標', value_name='分數')
        fig_line = px.line(df_melted, x='年份', y='分數', color='營運指標', markers=True, title='各項營運指標長期趨勢追蹤')
        fig_line.update_layout(yaxis=dict(range=[0, 100]))
        st.plotly_chart(fig_line, use_container_width=True)

    with tab3:
        st.subheader("💸 財務沙盤推演 (ROI Simulator)")
        st.info(f"您目前共有 **{total_budget:,.1f} 百萬** 的籌碼可以分配。")
        
        sim_cols = st.columns(4)
        sim_allocs = []
        for i, cat in enumerate(categories):
            with sim_cols[i]:
                # 🌟 完全解除預算封印，支援千億天文數字
                val = st.number_input(
                    f"投入【{cat}】(百萬)", 
                    min_value=0.0, 
                    max_value=None, 
                    value=float(alloc_dict[cat]), 
                    step=1000.0, 
                    format="%.1f", 
                    key=f"sim_{i}"
                )
                sim_allocs.append(val)
                
        # 🌟 動態監聽數字變化，只要一改數字，舊報告立刻清空！
        current_inputs = "_".join(map(str, sim_allocs))
        if st.session_state["last_sim_inputs"] != current_inputs:
            st.session_state["finance_ai_report"] = None
            st.session_state["last_sim_inputs"] = current_inputs

        total_sim = sum(sim_allocs)
        k_factors = np.array([1.5, 2.0, 1.2, 1.0])
        predicted_scores = np.clip(curr_scores + k_factors * np.sqrt(sim_allocs), 0, 100)
        loss_factors = [2.5, 3.0, 1.8, 0.5]
        current_loss = np.sum((100 - curr_scores) * loss_factors)
        predicted_loss = np.sum((100 - predicted_scores) * loss_factors)
        saved_money = current_loss - predicted_loss
        
        if total_sim > total_budget:
            st.error(f"⚠️ 預算超支！您分配了 {total_sim:,.1f} 百萬，總預算只有 {total_budget:,.1f} 百萬。")
        else:
            loss_cols = st.columns(2)
            with loss_cols[0]:
                st.metric("🔴 目前預估年度隱性損失", f"{current_loss:,.1f} 百萬")
            with loss_cols[1]:
                st.metric("🟢 模擬後預估隱性損失", f"{predicted_loss:,.1f} 百萬", f"為公司挽回: {saved_money:,.1f} 百萬", delta_color="normal")

            fig_sim = go.Figure()
            fig_sim.add_trace(go.Scatterpolar(r=[100]*5, theta=categories+[categories[0]], fill=None, name='目標標準', line=dict(color='mediumseagreen', dash='dash')))
            fig_sim.add_trace(go.Scatterpolar(r=list(curr_scores)+[curr_scores[0]], theta=categories+[categories[0]], fill='toself', name='本年度現況', line_color='rgba(150, 150, 150, 0.5)'))
            fig_sim.add_trace(go.Scatterpolar(r=list(predicted_scores)+[predicted_scores[0]], theta=categories+[categories[0]], fill='toself', name='明年度預測', line_color='mediumseagreen', fillcolor='rgba(46, 204, 113, 0.3)'))
            fig_sim.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), margin=dict(l=40, r=40, t=30, b=30))
            st.plotly_chart(fig_sim, use_container_width=True)

        st.divider()
        st.markdown("### 🤖 AI 財務深度診斷與改善建議")
        
        if st.button("✨ 立即生成 AI 財務分析報告", type="primary", key="btn_finance_ai"):
            if not api_key:
                st.error("⚠️ 缺少 OpenAI API Key，無法啟動財務分析。")
            else:
                with st.spinner("AI 正在結算最新財務模型與營運數據..."):
                    try:
                        from openai import OpenAI
                        client = OpenAI(api_key=api_key)
                        finance_prompt = f"""
                        你是一位擁有 20 年經驗的「航空公司營運與財務戰略幕僚」。
                        [模擬投資後預期 (總計投入 {total_sim:,.1f} M)] 預測飛安:{predicted_scores[0]:.1f}, 預測維修:{predicted_scores[1]:.1f}, 預測調度:{predicted_scores[2]:.1f}, 預測服務:{predicted_scores[3]:.1f} | 模擬後隱性損失：{predicted_loss:,.1f} M (成功挽回 {saved_money:,.1f} M)
                        請條列說明：1. 🔴 當前嚴重虧損主因。 2. 🟢 投資挽回損失的槓桿效應。 3. 🛠️ 具體營運改善建議。
                        """
                        response = client.chat.completions.create(
                            model="gpt-4o-mini", messages=[{"role": "user", "content": finance_prompt}], temperature=0.7
                        )
                        st.session_state["finance_ai_report"] = response.choices[0].message.content
                    except Exception as e:
                        st.error(f"⚠️ 產生失敗: {e}")

        if st.session_state["finance_ai_report"]:
            st.info(st.session_state["finance_ai_report"])

    # ==========================================
    # 🌍 API 與地圖定義
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
            geolocator = Nominatim(user_agent="airline_dash")
            loc = geolocator.geocode(search_query, timeout=5)
            if loc: return loc.latitude, loc.longitude
        except: pass
        return None, None

    @st.cache_data(ttl=600, show_spinner=False)
    def get_warzone_alerts(zone_name):
        try:
            if "烏俄" in zone_name: search_kw = "烏克蘭 OR 俄羅斯 OR 基輔"
            elif "葉門" in zone_name: search_kw = "紅海 OR 葉門 OR 青年運動"
            elif "以/巴" in zone_name: search_kw = "伊朗 OR 以色列 OR 敘利亞 OR 黎巴嫩"
            else: search_kw = "空襲 OR 戰爭"
            
            threat_keywords = ['空襲', '交戰', '防空', '擊落', '爆炸', '攻擊', '戰機', '飛彈']
            query = f"({search_kw}) AND ({' OR '.join(threat_keywords)}) when:7d"
            safe_query = urllib.parse.quote(query)
            url = f"https://news.google.com/rss/search?q={safe_query}&hl=zh-TW&gl=TW&ceid=TW:zh-Hant"
            feed = feedparser.parse(url)
            
            alerts = []
            for entry in feed.entries:
                title_lower = entry.title.lower()
                
                # 🌟 NLP 負面表列過濾器
                exclusions = [
                    '部署', '配備', '政策', '反擊', '研發', '採購', '試射', '軍售', '合約', '升級', '庫存', 
                    '小說', '電影', '遊戲', '劇', '年前', '演習', '演練', '測試', '速寫', '回顧', '歷史', '紀念', '模擬'
                ]
                if any(x in title_lower for x in exclusions): continue
                
                # 🌟 語意切割驗證
                segments = title_lower.replace('｜', '|').replace('；', '|').replace(' - ', '|').split('|')
                is_real_threat = False
                for seg in segments:
                    if any(k in seg for k in threat_keywords):
                        is_real_threat = True
                        break
                
                if not is_real_threat and len(segments) == 1 and len(title_lower) < 60: 
                    is_real_threat = True
                    
                if is_real_threat:
                    clean_title = entry.title.rsplit(' - ', 1)[0]
                    pub_date = entry.published if 'published' in entry else ""
                    alerts.append({"title": clean_title, "date": pub_date, "link": entry.link})
                    
                if len(alerts) >= 3: break
            return alerts
        except: return []

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

    with tab4:
        st.subheader("🌍 全球即時威脅圖 與 航線風險分析")
        airport_presets = ["TPE (台北 桃園機場)", "NRT (東京 成田機場)", "SIN (新加坡 樟宜機場)", "FRA (法蘭克福機場)", "LHR (倫敦 希斯洛機場)", "JFK (紐約 甘迺迪機場)", "LAX (洛杉磯機場)", "DXB (杜拜機場)", "SYD (雪梨機場)"]
        route_col1, route_col2 = st.columns(2)
        with route_col1: 
            origin_sel = st.selectbox("🛫 選擇起飛機場 (Origin)", airport_presets, index=0)
        with route_col2: 
            dest_sel = st.selectbox("🛬 選擇降落機場 (Destination)", airport_presets, index=1)

        if origin_sel and dest_sel:
            with st.spinner('📡 正在定位座標並計算物理碰撞預警...'):
                o_lat, o_lon = get_lat_lon(origin_sel)
                d_lat, d_lon = get_lat_lon(dest_sel)

            if o_lat and d_lat and (o_lat != d_lat or o_lon != d_lon):
                mid_lat, mid_lon = (o_lat + d_lat) / 2, (o_lon + d_lon) / 2
                
                # 🌟 實體交戰區定義 (錨定經緯度)
                actual_conflict_zones = [
                    {"name": "⚠️ 東歐交戰區 (烏俄)", "lat": 48.0, "lon": 37.0, "radius_size": 150, "threat_deg": 12.0}, 
                    {"name": "⚠️ 紅海區域威脅 (葉門)", "lat": 15.0, "lon": 42.0, "radius_size": 100, "threat_deg": 10.0}, 
                    {"name": "⚠️ 中東高度警戒區 (以/巴/伊/敘)", "lat": 34.0, "lon": 44.0, "radius_size": 180, "threat_deg": 15.0}   
                ]

                # 🌟 絕對精準的幾何物理碰撞演算法 (判斷航線是否切入紅圈)
                is_route_dangerous = False
                triggered_zone_name = ""
                for i in range(21):
                    f = i / 20.0
                    c_lat, c_lon = o_lat + (d_lat - o_lat) * f, o_lon + (d_lon - o_lon) * f
                    for zone in actual_conflict_zones:
                        if np.sqrt((c_lat - zone["lat"])**2 + (c_lon - zone["lon"])**2) < zone["threat_deg"]:
                            is_route_dangerous = True
                            triggered_zone_name = zone["name"]
                            break
                    if is_route_dangerous: 
                        break

                detour_lat = max(min(mid_lat - 20, 89.0), -89.0)
                detour_lon = mid_lon + 20 if mid_lon + 20 <= 180 else mid_lon + 20 - 360

                fig_map = go.Figure()
                
                # 繪製真實紅區
                for zone in actual_conflict_zones:
                    fig_map.add_trace(go.Scattergeo(
                        lat=[zone["lat"]], lon=[zone["lon"]],
                        marker=dict(size=zone["radius_size"], color='red', opacity=0.15, line=dict(width=1, color='darkred')),
                        name=zone["name"], mode="markers", text=zone["name"], hoverinfo="text"
                    ))

                # 動態航線畫線
                fig_map.add_trace(go.Scattergeo(
                    lat=[o_lat, d_lat] if not is_route_dangerous else [o_lat, mid_lat, d_lat], 
                    lon=[o_lon, d_lon] if not is_route_dangerous else [o_lon, mid_lon, d_lon],
                    mode='lines+markers', 
                    line=dict(width=3, color='red' if is_route_dangerous else 'mediumseagreen', dash='dot' if is_route_dangerous else 'solid'),
                    name="原訂航線 (高風險)" if is_route_dangerous else "標準航線 (安全)", 
                    text=[origin_sel[:5], dest_sel[:5]] if not is_route_dangerous else [origin_sel[:5], "Danger Zone", dest_sel[:5]]
                ))

                if is_route_dangerous:
                    fig_map.add_trace(go.Scattergeo(
                        lat=[o_lat, detour_lat, d_lat], lon=[o_lon, detour_lon, d_lon],
                        mode='lines+markers', line=dict(width=3, color='mediumseagreen'),
                        name="備用航線 (安全繞飛)"
                    ))

                # 🌟 修復白字高亮圖例
                fig_map.update_geos(
                    projection_type="natural earth", showcountries=True, countrycolor="RebeccaPurple",
                    showland=True, landcolor="rgb(30, 30, 30)", oceancolor="rgb(10, 10, 20)", showocean=True,
                    lataxis_range=[min(o_lat, d_lat, detour_lat if is_route_dangerous else d_lat)-15, max(o_lat, d_lat, detour_lat if is_route_dangerous else d_lat)+15], 
                    lonaxis_range=[min(o_lon, d_lon, detour_lon if is_route_dangerous else d_lon)-15, max(o_lon, d_lon, detour_lon if is_route_dangerous else d_lon)+15]
                )
                fig_map.update_layout(
                    height=500, margin=dict(l=0, r=0, t=30, b=0), paper_bgcolor="rgb(10, 10, 10)", 
                    legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01, font=dict(color="white", size=14))
                )
                st.plotly_chart(fig_map, use_container_width=True)
                st.divider()

                map_col1, map_col2 = st.columns(2)
                with map_col1:
                    if is_route_dangerous:
                        st.error(f"### 🚨 警告：物理切入實體交戰區 ({triggered_zone_name})")
                        live_alerts = get_warzone_alerts(triggered_zone_name)
                        if live_alerts:
                            for idx, alert in enumerate(live_alerts):
                                st.markdown(f"<div style='background-color: rgba(255, 75, 75, 0.1); padding:10px; border-left:4px solid #ff4b4b; margin-bottom:10px; border-radius:5px;'><strong style='color:#ff4b4b;'>[情報 {idx+1}]</strong> <span style='color: var(--text-color); font-weight: bold;'>{alert['title']}</span></div>", unsafe_allow_html=True)
                    else:
                        st.success(f"### 🛡️ 空域狀態評估：安全")
                        st.success("✅ 經幾何比對，本航路未觸及全球現有之武裝交戰區。")

                with map_col2:
                    if is_route_dangerous:
                        st.warning("### ⚠️ 系統建議：啟用繞道")
                        btn_col1, btn_col2 = st.columns(2)
                        with btn_col1: 
                            st.button("❌ 拒絕此航線", type="primary")
                        with btn_col2: 
                            st.button("✅ 批准繞道")
                    else:
                        st.success("### ✅ 航路安全評估通過")
                        st.button("✅ 依原計畫簽派 (Standard Dispatch)", type="primary")

    with tab5:
        st.subheader("🤖 AI 戰略幕僚 (Virtual Advisor)")
        st.info(f"🧠 **系統 Context 已同步**：內外部數據 皆已連線。")
        uq = st.chat_input("請輸入戰略問題...")
        if uq:
            st.chat_message("user").write(uq)
            with st.chat_message("assistant"):
                if not api_key: 
                    st.error("⚠️ 缺少 OpenAI API Key")
                else:
                    try:
                        from openai import OpenAI
                        client = OpenAI(api_key=api_key)
                        response = client.chat.completions.create(
                            model="gpt-4o-mini",
                            messages=[{"role": "system", "content": f"航線：{origin_sel} 到 {dest_sel}。請提供專業航空營運分析。"}, {"role": "user", "content": uq}],
                            temperature=0.7
                        )
                        st.write(response.choices[0].message.content)
                    except: 
                        st.error("⚠️ AI 幕僚連線失敗")

    # ==========================================
    # 🌟 報表生成模組：移至全域最底部，確保能精準捕捉您輸入的最新預算！
    # ==========================================
    # 確保在生成報表前，sim_allocs 等變數已經在 Tab 3 被計算出來
    try:
        current_total_sim = total_sim
        allocs = sim_allocs
        saved = saved_money
    except NameError:
        # 如果使用者還沒切換到 Tab 3 去初始化這些變數，先給預設值防呆
        current_total_sim = total_budget
        allocs = list(alloc_dict.values())
        saved = 0.0

    report_content = f"""# 航空公司年度營運診斷與資源最佳化報告
**報告生成時間：** {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    
## 一、 高階主管沙盤推演配置 (動態連動)
- 總投入資金：**{current_total_sim:,.1f} 百萬台幣**
- 飛安控管投入：{allocs[0]:,.1f} 百萬
- 機隊維修投入：{allocs[1]:,.1f} 百萬
- 航班調度投入：{allocs[2]:,.1f} 百萬
- 旅客服務投入：{allocs[3]:,.1f} 百萬
    
**預估財務成效：** 透過本次資源重分配，預估可為公司減少隱性損失高達 **{saved:,.1f} 百萬台幣**！

## 二、 深度專家診斷與改善行動方案\n"""

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
    st.sidebar.download_button(
        label="📄 匯出最新營運診斷書 (動態連動版)", 
        data=report_content, 
        file_name="Airline_Operations_Report.md", 
        mime="text/markdown"
    )
