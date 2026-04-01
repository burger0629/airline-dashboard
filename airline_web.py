import streamlit as st
import numpy as np
import plotly.graph_objects as go

# 設定網頁版面 (寬版)
st.set_page_config(page_title="航空公司營運診斷系統", layout="wide")

# ==========================================
# 網頁標題與側邊欄 (輸入區)
# ==========================================
st.title("✈️ 航空公司年度營運診斷與資源最佳化系統")
st.markdown("系統已啟用三級風險管理機制：**【0-60 非常嚴重】**、**【60-80 危險】**、**【80-100 安全】**")

st.sidebar.header("📊 營運指標數據輸入")
score_safety = st.sidebar.slider("1. 飛安綜合風險控管分數", 0.0, 100.0, 70.0)
score_maintenance = st.sidebar.slider("2. 機隊妥善與維修量能分數", 0.0, 100.0, 55.0)
score_otp = st.sidebar.slider("3. 航班準點率 (OTP) 分數", 0.0, 100.0, 85.0)
score_service = st.sidebar.slider("4. 旅客服務滿意度分數", 0.0, 100.0, 90.0)

st.sidebar.divider()
total_budget_millions = st.sidebar.number_input("💰 系統可用總預算 (百萬台幣)", min_value=10.0, max_value=5000.0, value=500.0)

# ==========================================
# 核心演算法：最佳化資源分配
# ==========================================
weights = {'飛安控管': 0.40, '機隊維修': 0.30, '航班調度': 0.20, '旅客服務': 0.10}
scores = {'飛安控管': score_safety, '機隊維修': score_maintenance, '航班調度': score_otp, '旅客服務': score_service}

total_urgency = 0
urgency_scores = {}
for cat, score in scores.items():
    gap = max(100.0 - score, 1.0)
    urgency = gap * weights[cat]
    urgency_scores[cat] = urgency
    total_urgency += urgency

allocations = {cat: (urgency_scores[cat] / total_urgency) * total_budget_millions for cat in scores}

# ==========================================
# 數據視覺化 (雷達圖與財務分配)
# ==========================================
col1, col2 = st.columns(2)

with col1:
    st.subheader("營運健康診斷雷達圖")
    fig = go.Figure()
    categories = list(scores.keys())
    values = list(scores.values())
    fig.add_trace(go.Scatterpolar(r=values + [values[0]], theta=categories + [categories[0]], fill='toself', name='當前體質', line_color='royalblue'))
    fig.add_trace(go.Scatterpolar(r=[100]*5, theta=categories + [categories[0]], name='目標標準', line=dict(color='mediumseagreen', dash='dash')))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), margin=dict(l=40, r=40, t=20, b=20))
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("💡 預算分配建議")
    st.info(f"**年度總預算： {total_budget_millions:,.1f} 百萬**")
    for cat in scores:
        st.metric(label=f"{cat}", value=f"{allocations[cat]:.1f} 百萬", delta=f"{scores[cat]:.1f} 分")

# ==========================================
# 🛠️ 自訂 UI 元件：美化版診斷卡片
# ==========================================
def render_diagnosis_card(category, score, level, advices):
    # 根據風險等級設定專屬的 CSS 顏色與標籤
    if level == 'critical':
        bg_color = "#3a0000" if st.get_option("theme.base") == "dark" else "#fff0f0"
        border_color = "#ff4b4b"
        text_color = "#ff4b4b" if st.get_option("theme.base") == "dark" else "#900000"
        icon = "🚨"
        status_text = "非常嚴重 (CRITICAL) —— 需立即採取阻斷性與懲罰性行動"
    elif level == 'warning':
        bg_color = "#332b00" if st.get_option("theme.base") == "dark" else "#fffbe6"
        border_color = "#ffc107"
        text_color = "#ffc107" if st.get_option("theme.base") == "dark" else "#856404"
        icon = "⚠️"
        status_text = "危險警告 (WARNING) —— 需啟動預防與加強防護機制"
    else:
        bg_color = "#002b12" if st.get_option("theme.base") == "dark" else "#f0fff4"
        border_color = "#28a745"
        text_color = "#28a745" if st.get_option("theme.base") == "dark" else "#155724"
        icon = "✅"
        status_text = "安全穩定 (SAFE) —— 維持現狀、深植安全文化與持續優化"

    # 輸出帶有強烈視覺色彩的 HTML 卡片標頭
    st.markdown(f"""
    <div style="background-color:{bg_color}; padding:20px; border-radius:10px; border-left: 10px solid {border_color}; margin-top: 20px; margin-bottom: 15px; box-shadow: 2px 2px 5px rgba(0,0,0,0.1);">
        <h3 style="color:{text_color}; margin-top:0; font-size: 1.5em;">{icon} {category} | 系統評估得分：<span style="font-size: 1.3em; font-weight: 900;">{score:.1f}</span> / 100</h3>
        <p style="color:{text_color}; font-weight:bold; margin-bottom:0; font-size: 1.1em;">狀態判定：{status_text}</p>
    </div>
    """, unsafe_allow_html=True)

    # 輸出詳細改善建議清單
    for idx, advice in enumerate(advices):
        st.markdown(f"**{idx+1}.** {advice}")
    st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# 🛠️ 專業知識庫與動態建議渲染
# ==========================================
st.divider()
st.subheader("📋 各領域專案改善行動書 (Action Plans)")

knowledge_base = {
    '飛安控管': {
        'critical': [
            "**[立即處置]** 暫停高風險/易受天氣干擾之航線運行，啟動全機隊安全停飛檢查 (Safety Stand-down)。", 
            "**[系統對策]** 檢視安全管理系統 (SMS) 中『瑞士起司模型』的防禦斷層，重新審計組織層級的系統性漏洞。", 
            "**[外部介入]** 成立緊急應變小組 (Task Force)，向主管機關提交自願改善計畫並接受第三方專案稽核。"
        ],
        'warning': [
            "**[主動防禦]** 增加航線檢查 (Line Check) 頻率，全面強化組員資源管理 (CRM) 訓練。", 
            "**[數據監控]** 擴大飛行數據監測 (FOQA) 之分析深度，提前辨識機隊潛在的不安全操作趨勢。", 
            "**[疲勞管理]** 嚴格檢視疲勞風險管理系統 (FRMS)，避免合法但不合理的班表安排。"
        ],
        'safe': [
            "**[文化深耕]** 系統運作穩健。請持續鼓勵基層的『公正文化 (Just Culture)』自願通報機制。", 
            "**[演練優化]** 策劃高強度的年度無預警安全演習，維持組織對極端事件的應變肌肉記憶。"
        ]
    },
    '機隊維修': {
        'critical': [
            "**[立即處置]** 針對妥善率低於標準之機型，強制執行適航指令 (AD) 深度檢查，必要時暫時將老舊機型除役。", 
            "**[人為因素]** 全面重新考核維修人員技術執照，嚴格取締違反 SOP 之『捷徑行為 (Workarounds)』。", 
            "**[供應鏈]** 盤點關鍵航材供應鏈斷鏈風險，立即動用緊急預算採購備用料件 (AOG spares)。"
        ],
        'warning': [
            "**[防護機制]** 針對高頻率故障的航電系統與發動機，主動縮短其預防性更換週期。", 
            "**[人為因素]** 於維修廠區強化『人為因素 (Human Factors)』之視覺化提醒，防範溝通不良或交接遺漏。", 
            "**[數位轉型]** 加速淘汰紙本維修紀錄，全面落實數位化追蹤以提升可追溯性。"
        ],
        'safe': [
            "**[持續維運]** 維修量能充足。請持續落實各機隊之例行 A、B、C、D 檢。", 
            "**[前瞻規劃]** 系統建議可撥用部分預算，先期導入 AI 預測性維修 (Predictive Maintenance) 模型驗證。"
        ]
    },
    '航班調度': {
        'critical': [
            "**[立即處置]** 大幅砍減延誤率過高之航班（即所謂的『紙上航班』），重新設計符合真實運能的時刻表。", 
            "**[資源重分配]** 盤點備用航機與空勤組員之真實缺口，強制縮減營運規模以匹配現行可動用資源。", 
            "**[節點控管]** 針對經常性塞機或地停效率極差的樞紐機場，暫緩新航權與時帶 (Slot) 申請。"
        ],
        'warning': [
            "**[效率優化]** 應用線性規劃模型，重新計算機場地停作業的關鍵路徑 (Critical Path)，減少閒置時間。", 
            "**[緩衝機制]** 於重點樞紐機場增加預備機 (Spare Aircraft) 與預備組員 (Standby) 指派基數。", 
            "**[協同決策]** 與氣象單位及航管單位建立 A-CDM (機場協同決策) 連線，提升面對突發天候的調度彈性。"
        ],
        'safe': [
            "**[持續維運]** 準點率指標優良，調度資源充沛。", 
            "**[精益管理]** 在確保準點率的前提下，可開始針對飛行計畫進行燃油經濟性 (Fuel Efficiency) 之最佳化微調。"
        ]
    },
    '旅客服務': {
        'critical': [
            "**[立即處置]** 針對客訴激增之接觸點 (Touchpoints) 啟動緊急服務補救專案，防止品牌形象災難性崩潰。", 
            "**[流程再造]** 重新修訂異常航班 (IRROPS) 發生時的旅客安置與補償 SOP，消弭前線人員的決策模糊地帶。", 
            "**[外部稽核]** 評估汰換履約成效極差之第三方地勤或餐飲代理商。"
        ],
        'warning': [
            "**[前線賦能]** 增加第一線地勤與空服人員針對『憤怒旅客安撫』之實境模擬訓練，並適度下放補償授權。", 
            "**[資訊透明]** 強化官網與 APP 推播系統，確保航班異動第一時間主動通知旅客，降低不確定感。", 
            "**[根因分析]** 針對次級客訴進行深度的根本原因分析 (Root Cause Analysis)，找出服務斷點。"
        ],
        'safe': [
            "**[持續維運]** 旅客滿意度維持高檔，第一線服務品質穩定。", 
            "**[價值提升]** 建議將資源投入常客忠誠度計畫 (FFP) 之個人化行銷，進一步提升高收益之商務客回流率。"
        ]
    }
}

# 動態渲染各項目的診斷報告
for cat, score in scores.items():
    if score < 60:
        render_diagnosis_card(cat, score, 'critical', knowledge_base[cat]['critical'])
    elif score < 80:
        render_diagnosis_card(cat, score, 'warning', knowledge_base[cat]['warning'])
    else:
        render_diagnosis_card(cat, score, 'safe', knowledge_base[cat]['safe'])
