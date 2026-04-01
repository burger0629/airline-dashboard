import streamlit as st
import numpy as np
import plotly.graph_objects as go

# 設定網頁版面 (寬版)
st.set_page_config(page_title="航空公司營運診斷系統", layout="wide")

st.title("✈️ 航空公司營運診斷與歷史趨勢對比系統")
st.markdown("本系統已整合 **年度對比功能**，自動分析各項指標之進退步幅度並給予動態決策建議。")

# ==========================================
# 網頁側邊欄 (數據輸入區)
# ==========================================
st.sidebar.header("📅 年度指標對比輸入")

# 當年數據
st.sidebar.subheader("【本年度 (Current Year)】")
curr_safety = st.sidebar.slider("1. 飛安控管 (今年)", 0, 100, 75)
curr_maint = st.sidebar.slider("2. 機隊維修 (今年)", 0, 100, 65)
curr_otp = st.sidebar.slider("3. 航班調度 (今年)", 0, 100, 85)
curr_service = st.sidebar.slider("4. 旅客服務 (今年)", 0, 100, 90)

st.sidebar.divider()

# 去年數據 (預設值設為稍微不同，方便觀察對比)
st.sidebar.subheader("【前年度 (Last Year)】")
prev_safety = st.sidebar.slider("1. 飛安控管 (去年)", 0, 100, 85)
prev_maint = st.sidebar.slider("2. 機隊維修 (去年)", 0, 100, 60)
prev_otp = st.sidebar.slider("3. 航班調度 (去年)", 0, 100, 80)
prev_service = st.sidebar.slider("4. 旅客服務 (去年)", 0, 100, 95)

st.sidebar.divider()
total_budget = st.sidebar.number_input("💰 系統可用總預算 (百萬台幣)", min_value=10.0, value=500.0)

# 數據結構化
categories = ['飛安控管', '機隊維修', '航班調度', '旅客服務']
curr_scores = [curr_safety, curr_maint, curr_otp, curr_service]
prev_scores = [prev_safety, prev_maint, prev_otp, prev_service]

# ==========================================
# 核心演算法：最佳化資源分配 (基於今年分數)
# ==========================================
weights = {'飛安控管': 0.40, '機隊維修': 0.30, '航班調度': 0.20, '旅客服務': 0.10}
urgency_scores = {}
total_urgency = 0

for i, cat in enumerate(categories):
    gap = max(100.0 - curr_scores[i], 1.0)
    urg = gap * weights[cat]
    urgency_scores[cat] = urg
    total_urgency += urg

allocations = {cat: (urgency_scores[cat] / total_urgency) * total_budget for cat in categories}

# ==========================================
# 視覺化呈現：雙雷達圖與年度指標對比
# ==========================================
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("🔄 年度營運體質對比雷達圖")
    fig = go.Figure()

    # 繪製前年度數據 (淺灰色填滿)
    fig.add_trace(go.Scatterpolar(
        r=prev_scores + [prev_scores[0]],
        theta=categories + [categories[0]],
        fill='toself',
        name='前年度 (Last Year)',
        line_color='rgba(150, 150, 150, 0.5)',
        fillcolor='rgba(200, 200, 200, 0.3)'
    ))

    # 繪製本年度數據 (藍色粗線)
    fig.add_trace(go.Scatterpolar(
        r=curr_scores + [curr_scores[0]],
        theta=categories + [categories[0]],
        fill='toself',
        name='本年度 (Current Year)',
        line_color='royalblue',
        fillcolor='rgba(65, 105, 225, 0.2)'
    ))

    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=True,
        margin=dict(l=40, r=40, t=30, b=30)
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("📈 年度指標進退步分析 (YOY)")
    st.info(f"**預算總計： {total_budget:,.1f} 百萬**")
    
    # 使用 st.metric 的 delta 功能顯示進退步
    m_cols = st.columns(2)
    for i, cat in enumerate(categories):
        delta = curr_scores[i] - prev_scores[i]
        with m_cols[i % 2]:
            st.metric(label=cat, value=f"{curr_scores[i]} 分", delta=f"{delta} 分")
            st.caption(f"建議配預算: {allocations[cat]:.1f} 百萬")
            st.write("---")

# ==========================================
# 🛠️ 深度專家診斷報告 (帶有歷史趨勢分析)
# ==========================================
st.divider()
st.subheader("📋 趨勢診斷與具體改善行動方案")

# [此處保留之前設計的 Knowledge Base 邏輯，但增加趨勢判斷]
for i, cat in enumerate(categories):
    score = curr_scores[i]
    delta = score - prev_scores[i]
    
    # 判定顏色與狀態
    if score < 60:
        color, level, icon = "red", "critical", "🚨"
    elif score < 80:
        color, level, icon = "orange", "warning", "⚠️"
    else:
        color, level, icon = "green", "safe", "✅"

    # 趨勢註解
    if delta > 5:
        trend_msg = f"已較去年顯著進步 (+{delta})，請持續保持優化力道。"
    elif delta < -5:
        trend_msg = f"較去年嚴重衰退 ({delta})！需徹查資源是否斷鏈或管理出現真空。"
    else:
        trend_msg = "與去年相比變動不大，建議重新評估目前投入之資源效能。"

    # 渲染卡片 (簡化版呈現以適應對比)
    with st.expander(f"{icon} {cat} | 分數: {score} ({trend_msg})", expanded=(score < 80)):
        if score < 80:
            st.markdown(f"**🔍 趨勢分析：** {trend_msg}")
            st.markdown("**🛠️ 核心改善方案：**")
            # 這裡可以根據不同 cat 給予對應的專業建議 (延用前次內容)
            if cat == '飛安控管':
                st.write("- 啟動主動式數據監測 (FOQA)，分析本年度出現的偏差行為趨勢。")
                st.write("- 強化組員資源管理 (CRM) 訓練，補足年度對比中下滑的警覺性指標。")
            elif cat == '機隊維修':
                st.write("- 針對進度落後的維修項目，優先撥付預算採購高消耗性航材。")
                st.write("- 重新評估老舊機型之維護成本，評估提前汰換計畫。")
            # ... 其他項目可依此類推
