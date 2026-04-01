import streamlit as st
import numpy as np
import plotly.graph_objects as go

# 設定網頁版面
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
# 🛠️ 三級風險專家診斷模組
# ==========================================
st.divider()
st.subheader("🛠️ 各項目風險等級診斷與改善行動方案")

# 定義專業建議數據庫
knowledge_base = {
    '飛安控管': {
        'critical': ["🚨 **立即強制行動**：暫停高風險航線運行，啟動全機隊安全停飛檢查 (Safety Stand-down)。", "成立緊急應變小組 (Task Force)，重新審計所有安全管理流程漏洞。", "向民航主管機關提交自願改善計畫，並接受外部專案稽核。"],
        'warning': ["⚠️ **加強防範行動**：增加航線檢查 (Line Check) 頻率，強化組員資源管理 (CRM) 訓練。", "啟動主動式數據監測 (FOQA)，分析潛在不安全趨勢。", "檢視疲勞風險管理系統 (FRMS)，優化排班間隔。"],
        'safe': ["✅ **持續監測行動**：維持現有 SMS 運作，並鼓勵基層通報文化 (Just Culture)。", "進行年度例行性安全演習，維持應變量能。"]
    },
    '機隊維修': {
        'critical': ["🚨 **立即強制行動**：對特定高機齡機型進行強制適航指令 (AD) 檢查，必要時暫時除役。", "檢查零件供應鏈是否出現系統性短缺，立即尋求備份料件來源。", "全面重新考核維修人員技術執照與 SOP 執行準確度。"],
        'warning': ["⚠️ **加強防範行動**：縮短發動機與關鍵航電設備的預防性更換週期。", "加強人為因素 (Human Factors) 訓練，減少維修過程的人為失誤。", "更新電子維修紀錄系統，提升數據追蹤透明度。"],
        'safe': ["✅ **持續監測行動**：落實例行 A、B、C、D 檢，確保各機隊妥善率穩定。", "評估導入預測性維修 (Predictive Maintenance) AI 技術。"]
    },
    '航班調度': {
        'critical': ["🚨 **立即強制行動**：大幅砍減延誤率過高之航班，重新設計時刻表容量限制。", "盤點備用航機與空勤組員缺口，強制縮減營運規模以匹配現有量能。", "針對經常性延誤的機場節點，暫停航權申請。"],
        'warning': ["⚠️ **加強防範行動**：應用線性規劃模型優化地停周轉時間 (Turnaround Time)。", "於樞紐機場增加預備機與預備組員 (Standby) 指派人數。", "與氣象單位強化連動，建立更靈敏的動態調度協議。"],
        'safe': ["✅ **持續監測行動**：維持高準點率紀錄，並分析如何進一步降低油耗。"]
    },
    '旅客服務': {
        'critical': ["🚨 **立即強制行動**：針對負面評價激增的環節，立即啟動服務補救專案。", "重新修訂異常航班處理補償標準，防止品牌形象災難性崩潰。", "對服務流程進行徹底再造 (BPR)，更換表現不佳的承包商。"],
        'warning': ["⚠️ **加強防範行動**：強化第一線人員情緒管理與危機溝通授權。", "增加數位客服投訴管道，縮短客訴回應時間 (TAT)。", "進行旅客滿意度深度分析，找出各航點服務不一的斷點。"],
        'safe': ["✅ **持續監測行動**：推動忠誠度計畫 (FFP) 優化，提升商務客回流率。"]
    }
}

for cat, score in scores.items():
    if score < 60:
        with st.error(f"🔴 【{cat}】 非常嚴重： 分數 {score:.1f} (低於 60 分基準)"):
            for advice in knowledge_base[cat]['critical']:
                st.markdown(advice)
    elif score < 80:
        with st.warning(f"🟡 【{cat}】 危險： 分數 {score:.1f} (介於 60-80 分區間)"):
            for advice in knowledge_base[cat]['warning']:
                st.markdown(advice)
    else:
        with st.success(f"🟢 【{cat}】 安全： 分數 {score:.1f} (高於 80 分標準)"):
            for advice in knowledge_base[cat]['safe']:
                st.markdown(advice)
