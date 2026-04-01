import streamlit as st
import numpy as np
import plotly.graph_objects as go

# 設定網頁版面 (寬版)
st.set_page_config(page_title="航空公司營運診斷系統", layout="wide")

st.title("✈️ 航空公司營運診斷與趨勢最佳化系統")
st.markdown("本系統已啟用 **六級風險色帶管理機制** 與 **深度根因分析行動書**，支援全環境深淺色自適應顯示。")

# ==========================================
# 網頁側邊欄 (數據輸入區)
# ==========================================
st.sidebar.header("📅 營運指標數據輸入")

st.sidebar.subheader("【本年度 (Current Year)】")
st.sidebar.markdown("*請利用滑桿調整當前營運分數 (0-100)*")
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

# 數據結構化
categories = ['飛安控管', '機隊維修', '航班調度', '旅客服務']
curr_scores = [curr_safety, curr_maint, curr_otp, curr_service]
prev_scores = [prev_safety, prev_maint, prev_otp, prev_service]
scores_dict = {'飛安控管': curr_safety, '機隊維修': curr_maint, '航班調度': curr_otp, '旅客服務': curr_service}

# ==========================================
# 核心演算法：最佳化資源分配 (基於今年分數)
# ==========================================
weights = {'飛安控管': 0.40, '機隊維修': 0.30, '航班調度': 0.20, '旅客服務': 0.10}
urgency_scores = {}
total_urgency = 0

for cat, score in scores_dict.items():
    gap = max(100.0 - score, 1.0)
    urg = gap * weights[cat]
    urgency_scores[cat] = urg
    total_urgency += urg

allocations = {cat: (urgency_scores[cat] / total_urgency) * total_budget for cat in categories}

# ==========================================
# 視覺化呈現：雙雷達圖與指標分析
# ==========================================
col1, col2 = st.columns([1.2, 1])

with col1:
    st.subheader("🔄 年度營運體質對比雷達圖")
    fig = go.Figure()

    # 繪製前年度數據
    fig.add_trace(go.Scatterpolar(
        r=prev_scores + [prev_scores[0]], theta=categories + [categories[0]],
        fill='toself', name='前年度 (Last Year)',
        line_color='rgba(150, 150, 150, 0.5)', fillcolor='rgba(200, 200, 200, 0.3)'
    ))

    # 繪製本年度數據
    fig.add_trace(go.Scatterpolar(
        r=curr_scores + [curr_scores[0]], theta=categories + [categories[0]],
        fill='toself', name='本年度 (Current Year)',
        line_color='royalblue', fillcolor='rgba(65, 105, 225, 0.2)'
    ))

    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), margin=dict(l=50, r=50, t=30, b=30))
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("📈 年度指標進退步與預算分配 (YOY)")
    st.info(f"**年度總預算： {total_budget:,.1f} 百萬**")
    
    m_cols = st.columns(2)
    for i, cat in enumerate(categories):
        delta = curr_scores[i] - prev_scores[i]
        with m_cols[i % 2]:
            st.metric(label=cat, value=f"{curr_scores[i]:.1f} 分", delta=f"{delta:.1f} 分")
            st.caption(f"💰 建議預算: **{allocations[cat]:.1f} 百萬**")
            st.write("---")

# ==========================================
# 🛠️ 自訂 UI 元件：六級風險科技感透明卡片
# ==========================================
def get_risk_level_config(score):
    """根據分數返回: (風險等級, 主題色, 判定文字)"""
    if score == 100.0:
        return ('perfect', "#00d26a", "🏆 卓越典範 (PERFECT) —— 系統處於理想狀態，維持卓越並分享經驗")
    elif score >= 81.0:
        return ('stable', "#28a745", "✅ 安全穩定 (STABLE) —— 績效優良，持續精益求精與深化文化")
    elif score >= 61.0:
        return ('caution', "#ffc107", "⚠️ 黃色警戒 (CAUTION) —— 績效輕微下滑，需啟動主動式數據監測")
    elif score >= 41.0:
        return ('serious', "#fd7e14", "🟠 橘色風險 (SERIOUS) —— 存在組織性漏洞，需深度重整與系統性對策")
    elif score >= 21.0:
        return ('high_risk', "#e74c3c", "🔴 紅色高危 (HIGH RISK) —— 系統防禦失效，需立即介入與危機處置")
    else: # 0-20
        return ('catastrophic', "#ff3333", "🚨 災難崩潰 (CATASTROPHIC) —— 組織機能癱瘓，立即停止營運並全面重審")

def render_diagnosis_card(category, score, delta):
    level, main_color, status_text = get_risk_level_config(score)
    
    # 動態趨勢評語
    if delta >= 10: trend_label = f"📈 跨越式進步 (+{delta:.1f})"
    elif delta > 0: trend_label = f"↗️ 微幅進步 (+{delta:.1f})"
    elif delta <= -10: trend_label = f"📉 潰雪式衰退 ({delta:.1f})"
    elif delta < 0: trend_label = f"↘️ 微幅下滑 ({delta:.1f})"
    else: trend_label = "➖ 表現持平"

    # 【設計變更】: 拿掉泥巴色的背景，改用全透明背景 (transparent)，並加上微微發光的細邊框
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

# ==========================================
# 🛠️ 六級深度專業知識庫 (Knowledge Base)
# ==========================================
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
# 🛠️ 動態渲染專家診斷報告
# ==========================================
st.divider()
st.subheader("📋 年度趨勢診斷報告與具體改善行動書 (Action Plans)")

for i, cat in enumerate(categories):
    curr_score = curr_scores[i]
    prev_score = prev_scores[i]
    delta = curr_score - prev_score
    
    # 渲染卡片並取得風險等級
    level = render_diagnosis_card(cat, curr_score, delta)

    # 展開詳細內容 (只展開有風險的類別)
    data = knowledge_base[cat][level]
    
    expanded = level not in ['perfect', 'stable']
    with st.expander(f"🔍 查看深度診斷分析報告...", expanded=expanded):
        
        # 危險與嚴重的類別，才顯示潛在根本原因
        if level in ['catastrophic', 'high_risk', 'serious', 'caution']:
            st.markdown(f"#### 🔍 潛在根本原因 (Root Cause)")
            for reason in data['reasons']:
                st.markdown(f"- 🚩 {reason}")
            st.markdown("---")
        
        # 所有類別都顯示行動方案
        st.markdown(f"#### 🛠️ 具體執行方案 (Action Plan)")
        for action in data['actions']:
            st.markdown(f"- {action}")
        
        st.markdown("<br>", unsafe_allow_html=True)
