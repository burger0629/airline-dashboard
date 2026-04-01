import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from scipy.optimize import minimize
import datetime

# 設定網頁版面 (寬版)
st.set_page_config(page_title="航空公司營運戰情室", layout="wide")

st.title("✈️ 航空公司營運戰情室 (Aviation War Room)")
st.markdown("整合 **六級風險深度診斷**、**作業研究最佳化**、**長期趨勢預測** 與 **動態航線風險評估** 的決策支援系統。")

# ==========================================
# 網頁側邊欄 (數據輸入)
# ==========================================
st.sidebar.header("📅 營運指標數據輸入")

st.sidebar.subheader("【本年度 (Current Year)】")
curr_safety = st.sidebar.slider("1. 飛安控管 (今年)", 0.0, 100.0, 75.0, step=1.0)
curr_maint = st.sidebar.slider("2. 機隊維修 (今年)", 0.0, 100.0, 15.0, step=1.0)
curr_otp = st.sidebar.slider("3. 航班調度 (今年)", 0.0, 100.0, 85.0, step=1.0)
curr_service = st.sidebar.slider("4. 旅客服務 (今年)", 0.0, 100.0, 100.0, step=1.0)

st.sidebar.divider()
st.sidebar.subheader("【前年度 (Last Year)】")
prev_safety = st.sidebar.slider("1. 飛安控管 (去年)", 0.0, 100.0, 85.0, step=1.0)
prev_maint = st.sidebar.slider("2. 機隊維修 (去年)", 0.0, 100.0, 60.0, step=1.0)
prev_otp = st.sidebar.slider("3. 航班調度 (去年)", 0.0, 100.0, 80.0, step=1.0)
prev_service = st.sidebar.slider("4. 旅客服務 (去年)", 0.0, 100.0, 95.0, step=1.0)

st.sidebar.divider()
total_budget = st.sidebar.number_input("💰 系統可用總預算 (百萬台幣)", min_value=10.0, value=500.0, step=10.0)

categories = ['飛安控管', '機隊維修', '航班調度', '旅客服務']
weights = np.array([0.40, 0.30, 0.20, 0.10])
curr_scores = np.array([curr_safety, curr_maint, curr_otp, curr_service])
prev_scores = np.array([prev_safety, prev_maint, prev_otp, prev_service])

# ==========================================
# 核心演算法：線性/非線性最佳化 (LP/NLP)
# ==========================================
def objective(x, current_scores, weights):
    k_factors = np.array([1.5, 2.0, 1.2, 1.0])
    new_scores = current_scores + k_factors * np.sqrt(x)
    new_scores = np.clip(new_scores, 0, 100)
    gaps = 100 - new_scores
    return np.sum(weights * gaps)

constraints = {'type': 'eq', 'fun': lambda x: np.sum(x) - total_budget}
bounds = tuple((total_budget * 0.02, total_budget) for _ in range(4))
initial_guess = np.array([total_budget/4]*4)

result = minimize(objective, initial_guess, args=(curr_scores, weights), method='SLSQP', bounds=bounds, constraints=constraints)
allocations = result.x if result.success else initial_guess
alloc_dict = {cat: alloc for cat, alloc in zip(categories, allocations)}

# ==========================================
# 一鍵匯出報表功能 (回歸！)
# ==========================================
report_content = f"""# 航空公司年度營運診斷與資源最佳化報告
**報告生成時間：** {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**總可用預算：** {total_budget} 百萬台幣

## 一、 年度指標進退步分析
"""
for i, cat in enumerate(categories):
    delta = curr_scores[i] - prev_scores[i]
    report_content += f"- **{cat}**：本年 {curr_scores[i]:.1f} 分 (去年 {prev_scores[i]:.1f} 分) | 變動：{delta:+.1f} 分\n"

report_content += "\n## 二、 最佳化預算配置建議\n"
for cat, alloc in alloc_dict.items():
    report_content += f"- **{cat}**：建議投入 {alloc:.1f} 百萬台幣\n"

st.sidebar.divider()
st.sidebar.download_button(
    label="📄 匯出年度營運診斷書 (Report)", 
    data=report_content, 
    file_name="Airline_Operations_Report.md", 
    mime="text/markdown"
)

# ==========================================
# UI 元件與六級知識庫設定
# ==========================================
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

    bg_color = main_color + "20" 
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
# 建立頁籤架構 (Tabs) 
# ==========================================
tab1, tab2, tab3, tab4 = st.tabs(["📊 核心診斷分配", "📈 長期趨勢 (檔案匯入)", "🔮 沙盤推演 (預測)", "🌍 航線風險評估 (自選)"])

with tab1:
    col1, col2 = st.columns([1.2, 1])
    with col1:
        st.subheader("🔄 年度營運體質對比雷達圖")
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(r=list(prev_scores)+[prev_scores[0]], theta=categories+[categories[0]], fill='toself', name='前年度', line_color='rgba(150, 150, 150, 0.5)'))
        fig.add_trace(go.Scatterpolar(r=list(curr_scores)+[curr_scores[0]], theta=categories+[categories[0]], fill='toself', name='本年度', line_color='royalblue', fillcolor='rgba(65, 105, 225, 0.2)'))
        fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), margin=dict(l=40, r=40, t=30, b=30))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("📈 年度指標與最佳化分配 (YOY)")
        m_cols = st.columns(2)
        for i, cat in enumerate(categories):
            delta = curr_scores[i] - prev_scores[i]
            with m_cols[i % 2]:
                st.metric(label=cat, value=f"{curr_scores[i]:.1f}", delta=f"{delta:.1f}")
                st.caption(f"💰 建議預算: **{alloc_dict[cat]:.1f} 百萬**")

    # 完整回歸的專家診斷展開區
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
    # 歷史營運資料與CSV上傳功能 (回歸！)
    st.subheader("📈 歷史營運數據趨勢分析 (五年期)")
    st.markdown("您可以上傳包含歷史數據的 CSV 檔案，或查看系統預設的模擬數據。")
    
    uploaded_file = st.file_uploader("📂 上傳歷史營運數據 (CSV)", type="csv")
    
    if uploaded_file is not None:
        df_trend = pd.read_csv(uploaded_file)
        st.success("檔案讀取成功！")
    else:
        years = ['2022', '2023', '2024', '2025', '2026(YTD)']
        df_trend = pd.DataFrame({
            '年份': years,
            '飛安控管': [92, 88, 85, prev_safety, curr_safety],
            '機隊維修': [80, 75, 65, prev_maint, curr_maint],
            '航班調度': [88, 85, 82, prev_otp, curr_otp],
            '旅客服務': [85, 90, 92, prev_service, curr_service]
        })
    
    # 繪製五年歷史趨勢折線圖
    df_melted = df_trend.melt(id_vars=['年份'], var_name='營運指標', value_name='分數')
    fig_line = px.line(df_melted, x='年份', y='分數', color='營運指標', markers=True, title='各項營運指標長期趨勢追蹤')
    fig_line.update_layout(yaxis=dict(range=[0, 100]))
    st.plotly_chart(fig_line, use_container_width=True)
    
    with st.expander("📄 查看詳細數據表格"):
        st.dataframe(df_trend, use_container_width=True)

with tab3:
    # 沙盤推演與預測模型 (回歸！)
    st.subheader("🔮 決策沙盤推演 (What-If Simulator)")
    st.markdown("手動調配預算，系統將利用 **邊際效益遞減模型** 反向推算明年度的預期營運分數。")
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
        st.success(f"預算分配完畢 (剩餘 {total_budget - total_sim} 百萬)。以下為系統預測之明年成績：")
        
        k_factors = np.array([1.5, 2.0, 1.2, 1.0])
        predicted_scores = np.clip(curr_scores + k_factors * np.sqrt(sim_allocs), 0, 100)
        
        # 繪製預測雷達圖
        fig_sim = go.Figure()
        fig_sim.add_trace(go.Scatterpolar(r=list(curr_scores)+[curr_scores[0]], theta=categories+[categories[0]], fill='toself', name='本年度 (現況)', line_color='rgba(150, 150, 150, 0.5)'))
        fig_sim.add_trace(go.Scatterpolar(r=list(predicted_scores)+[predicted_scores[0]], theta=categories+[categories[0]], fill='toself', name='明年度 (預測)', line_color='mediumseagreen', fillcolor='rgba(46, 204, 113, 0.3)'))
        fig_sim.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), margin=dict(l=40, r=40, t=30, b=30))
        
        sim_res_cols = st.columns([1, 1])
        with sim_res_cols[0]:
            st.plotly_chart(fig_sim, use_container_width=True)
        with sim_res_cols[1]:
            st.write("### 📈 預期效益分析")
            for i, cat in enumerate(categories):
                growth = predicted_scores[i] - curr_scores[i]
                st.metric(label=f"預測 {cat} 分數", value=f"{predicted_scores[i]:.1f} 分", delta=f"預期成長 {growth:+.1f} 分")

with tab4:
    # 航線風險評估模組 (包含下拉選單自訂起降)
    st.subheader("🌍 航線動態風險評估與重飛計畫 (Dynamic Routing)")
    st.markdown("串接全球情報與飛航公告 (NOTAMs)，動態計算航線衝突區並給予繞道成本評估。")
    
    airport_db = {
        'TPE (台北 桃園)': (25.07, 121.23),
        'NRT (東京 成田)': (35.77, 140.39),
        'SIN (新加坡 樟宜)': (1.36, 103.99),
        'FRA (法蘭克福)': (50.03, 8.57),
        'LHR (倫敦 希斯洛)': (51.47, -0.45),
        'JFK (紐約 甘迺迪)': (40.64, -73.77),
        'LAX (洛杉磯)': (33.94, -118.40),
        'DXB (杜拜)': (25.25, 55.36),
        'SYD (雪梨)': (-33.94, 151.17)
    }

    route_col1, route_col2 = st.columns(2)
    with route_col1:
        origin = st.selectbox("🛫 起飛機場 (Origin)", list(airport_db.keys()), index=0)
    with route_col2:
        destination = st.selectbox("🛬 降落機場 (Destination)", list(airport_db.keys()), index=3)

    if origin == destination:
        st.warning("⚠️ 起飛與降落機場不能相同，請重新選擇。")
    else:
        o_lat, o_lon = airport_db[origin]
        d_lat, d_lon = airport_db[destination]

        mid_lat = (o_lat + d_lat) / 2
        mid_lon = (o_lon + d_lon) / 2

        detour_lat = mid_lat - 15 
        detour_lon = mid_lon + 10

        fig_map = go.Figure()

        fig_map.add_trace(go.Scattergeo(
            lat=[mid_lat], lon=[mid_lon],
            marker=dict(size=90, color='red', opacity=0.3),
            name="🚨 模擬高風險管制區", mode="markers"
        ))

        fig_map.add_trace(go.Scattergeo(
            lat=[o_lat, mid_lat, d_lat],
            lon=[o_lon, mid_lon, d_lon],
            mode='lines+markers', line=dict(width=3, color='red', dash='dash'),
            name="原訂直飛航線 (高風險)", text=[origin[:3], "Danger Zone", destination[:3]], textposition="bottom center"
        ))

        fig_map.add_trace(go.Scattergeo(
            lat=[o_lat, detour_lat, d_lat],
            lon=[o_lon, detour_lon, d_lon],
            mode='lines+markers', line=dict(width=3, color='mediumseagreen'),
            name="建議備用航線 (安全繞飛)", text=[origin[:3], "Safe Waypoint", destination[:3]], textposition="bottom center"
        ))

        fig_map.update_geos(
            projection_type="natural earth",
            showcountries=True, countrycolor="RebeccaPurple",
            showland=True, landcolor="rgb(243, 243, 243)",
            lataxis_range=[-50, 80], lonaxis_range=[-150, 180]
        )
        fig_map.update_layout(height=500, margin=dict(l=0, r=0, t=30, b=0), legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01))
        st.plotly_chart(fig_map, use_container_width=True)

        map_col1, map_col2 = st.columns(2)
        with map_col1:
            st.error(f"### 🚨 原訂航線風險警告 ({origin[:3]} ✈️ {destination[:3]})")
            st.markdown(f"""
            **影響空域：** 座標 ({mid_lat:.1f}, {mid_lon:.1f}) 周邊 500 海浬
            - **🚩 地空飛彈威脅 (SAM)：** 該區域近期有未經公告之防空飛彈活動，存在誤擊民航機之極高風險。
            - **📡 GPS 欺騙干擾 (Spoofing)：** 近 48 小時內接獲多起民航機回報，該空域存在軍用級 GPS 訊號覆寫。
            - **📜 法規限制：** 主管機關已發布 NOTAM，強烈建議民航機避開此管制區。
            """)
            st.button("❌ 拒絕此航線 (Deny Route)", type="primary")

        with map_col2:
            st.success("### ✅ 系統建議：啟用動態安全繞道航線")
            st.markdown("""
            **改道路徑：** 系統已自動計算偏置航路 (Offset Route) 避開高風險管制區。
            - **🛡️ 飛安評估：** 避開所有交戰區，導航訊號穩定，天候狀況良好。
            """)
            
            st.markdown("#### 💰 繞道營運成本評估 (Delta Cost)")
            c1, c2, c3 = st.columns(3)
            c1.metric("增加飛行時間", f"+ {np.random.randint(45, 120)} 分鐘", delta_color="inverse")
            c2.metric("額外燃油消耗", f"+ {np.random.randint(5, 18)} 噸", delta_color="inverse")
            c3.metric("航班準點率影響", "延遲抵達", delta_color="inverse")
            
            st.button("✅ 批准並重新簽派 (Approve & Dispatch)")
