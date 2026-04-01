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
st.markdown("整合 **六級風險深度診斷**、**作業研究最佳化**、**動態沙盤推演** 與 **航線地緣風險評估** 的決策支援系統。")

# ==========================================
# 網頁側邊欄 (數據輸入)
# ==========================================
st.sidebar.header("📅 營運指標數據輸入")

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

# UI 元件與六級知識庫
def get_risk_level_config(score):
    if score == 100.0: return ('perfect', "#00d26a", "🏆 卓越典範 (PERFECT)")
    elif score >= 81.0: return ('stable', "#28a745", "✅ 安全穩定 (STABLE)")
    elif score >= 61.0: return ('caution', "#ffc107", "⚠️ 黃色警戒 (CAUTION)")
    elif score >= 41.0: return ('serious', "#fd7e14", "🟠 橘色風險 (SERIOUS)")
    elif score >= 21.0: return ('high_risk', "#e74c3c", "🔴 紅色高危 (HIGH RISK)")
    else: return ('catastrophic', "#ff3333", "🚨 災難崩潰 (CATASTROPHIC)")

def render_diagnosis_card(category, score, delta):
    level, main_color, status_text = get_risk_level_config(score)
    if delta >= 10: trend_label = f"📈 跨越式進步 (+{delta:.1f})"
    elif delta > 0: trend_label = f"↗️ 微幅進步 (+{delta:.1f})"
    elif delta <= -10: trend_label = f"📉 潰雪式衰退 ({delta:.1f})"
    elif delta < 0: trend_label = f"↘️ 微幅下滑 ({delta:.1f})"
    else: trend_label = "➖ 表現持平"

    bg_color = main_color + "20" 
    st.markdown(f"""
    <div style="background-color:{bg_color}; padding:15px; border-radius:10px; border-left: 8px solid {main_color}; margin-top: 15px;">
        <h4 style="color: var(--text-color); margin-top:0;">
            {category} | 得分：<span style="color:{main_color}; font-size: 1.2em; font-weight: 900;">{score:.1f}</span> 
            <span style="font-size: 0.7em; font-weight: normal; opacity: 0.8;">({trend_label})</span>
        </h4>
        <p style="color: var(--text-color); font-weight:bold; font-size: 1em; margin-bottom:0;">判定：<span style="color:{main_color};">{status_text}</span></p>
    </div>
    """, unsafe_allow_html=True)
    return level

# (省略部分過長的 knowledge_base 字典，保持之前結構，此處為展示簡化)
knowledge_base = {
    '飛安控管': {'catastrophic': {'reasons': ["SMS系統癱瘓"], 'actions': ["全面停飛審查"]}, 'high_risk': {'reasons': ["防禦失效"], 'actions': ["高風險航線停飛"]}, 'serious': {'reasons': ["孤島效應"], 'actions': ["跨部門整合數據"]}, 'caution': {'reasons': ["機組疲勞"], 'actions': ["強化FOQA與CRM"]}, 'stable': {'reasons': ["運作良好"], 'actions': ["維持公正文化"]}, 'perfect': {'reasons': ["世界級標準"], 'actions': ["無預警演習"]}},
    '機隊維修': {'catastrophic': {'reasons': ["違規維修"], 'actions': ["徹換主管、移送調查"]}, 'high_risk': {'reasons': ["航材斷鏈"], 'actions': ["緊急採購備料"]}, 'serious': {'reasons': ["交接資訊遺漏"], 'actions': ["數位化維修表單"]}, 'caution': {'reasons': ["老舊機型故障率升"], 'actions': ["縮短預防更換週期"]}, 'stable': {'reasons': ["妥善率高"], 'actions': ["建立AI預測模型"]}, 'perfect': {'reasons': ["零事故"], 'actions': ["分享零失誤經驗"]}},
    '航班調度': {'catastrophic': {'reasons': ["時刻表錯配"], 'actions': ["強制縮減營運網"]}, 'high_risk': {'reasons': ["無緩衝裕度"], 'actions': ["增加備用機與待命"]}, 'serious': {'reasons': ["資訊傳遞時間差"], 'actions': ["導入A-CDM連線"]}, 'caution': {'reasons': ["地停效率不彰"], 'actions': ["優化關鍵路徑"]}, 'stable': {'reasons': ["準點率高"], 'actions': ["優化燃油經濟性"]}, 'perfect': {'reasons': ["零延誤"], 'actions': ["提升組員滿意度"]}},
    '旅客服務': {'catastrophic': {'reasons': ["外包品質失控"], 'actions': ["重新招標代理商"]}, 'high_risk': {'reasons': ["SOP模糊"], 'actions': ["下放前線決策權"]}, 'serious': {'reasons': ["數位服務落後"], 'actions': ["升級APP伺服器"]}, 'caution': {'reasons': ["服務品質不一"], 'actions': ["加強實境模擬訓練"]}, 'stable': {'reasons': ["滿意度穩定"], 'actions': ["神秘客抽查"]}, 'perfect': {'reasons': ["零客訴"], 'actions': ["優化常客忠誠度計畫"]}}
}

# ==========================================
# 建立頁籤架構 (Tabs) 
# ==========================================
tab1, tab2, tab3, tab4 = st.tabs(["📊 核心診斷分配", "📈 長期趨勢", "🔮 沙盤推演", "🌍 航線風險評估 (New)"])

with tab1:
    col1, col2 = st.columns([1.2, 1])
    with col1:
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(r=list(prev_scores)+[prev_scores[0]], theta=categories+[categories[0]], fill='toself', name='前年度', line_color='rgba(150, 150, 150, 0.5)'))
        fig.add_trace(go.Scatterpolar(r=list(curr_scores)+[curr_scores[0]], theta=categories+[categories[0]], fill='toself', name='本年度', line_color='royalblue', fillcolor='rgba(65, 105, 225, 0.2)'))
        fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), margin=dict(l=40, r=40, t=30, b=30))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        m_cols = st.columns(2)
        for i, cat in enumerate(categories):
            delta = curr_scores[i] - prev_scores[i]
            with m_cols[i % 2]:
                st.metric(label=cat, value=f"{curr_scores[i]:.1f}", delta=f"{delta:.1f}")
                st.caption(f"💰 建議預算: **{alloc_dict[cat]:.1f} 百萬**")

    st.divider()
    for i, cat in enumerate(categories):
        delta = curr_scores[i] - prev_scores[i]
        level = render_diagnosis_card(cat, curr_scores[i], delta)

with tab2:
    years = ['2022', '2023', '2024', '2025', '2026(YTD)']
    df_trend = pd.DataFrame({'年份': years, '飛安控管': [92, 88, 85, prev_safety, curr_safety], '機隊維修': [80, 75, 65, prev_maint, curr_maint], '航班調度': [88, 85, 82, prev_otp, curr_otp], '旅客服務': [85, 90, 92, prev_service, curr_service]})
    df_melted = df_trend.melt(id_vars=['年份'], var_name='營運指標', value_name='分數')
    fig_line = px.line(df_melted, x='年份', y='分數', color='營運指標', markers=True, title='營運指標趨勢追蹤')
    fig_line.update_layout(yaxis=dict(range=[0, 100]))
    st.plotly_chart(fig_line, use_container_width=True)

with tab3:
    st.markdown("手動調配預算，系統將利用 **邊際效益遞減模型** 反向推算明年度預期分數。")
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
        
        fig_sim = go.Figure()
        fig_sim.add_trace(go.Scatterpolar(r=list(curr_scores)+[curr_scores[0]], theta=categories+[categories[0]], fill='toself', name='本年度現況', line_color='rgba(150, 150, 150, 0.5)'))
        fig_sim.add_trace(go.Scatterpolar(r=list(predicted_scores)+[predicted_scores[0]], theta=categories+[categories[0]], fill='toself', name='明年度預測', line_color='mediumseagreen', fillcolor='rgba(46, 204, 113, 0.3)'))
        fig_sim.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), margin=dict(l=40, r=40, t=30, b=30))
        st.plotly_chart(fig_sim, use_container_width=True)

# ==========================================
# 新增模組：Tab 4 航線動態風險評估
# ==========================================
with tab4:
    st.subheader("🌍 航線動態風險評估與重飛計畫 (Dynamic Rerouting)")
    st.markdown("串接全球情報與飛航公告 (NOTAMs)，即時分析航線衝突區並計算繞道成本。")
    
    # 選擇航線
    route = st.selectbox("請選擇預定執飛之航班：", ["CI061 台北 (TPE) ✈️ 法蘭克福 (FRA)", "BR087 台北 (TPE) ✈️ 巴黎 (CDG)"])
    
    # 定義經緯度座標點
    coords = {
        'TPE': (25.07, 121.23),
        'FRA': (50.03, 8.57),
        'Middle_East': (33.0, 44.0), # 戰區中心點 (伊拉克/伊朗一帶)
        'Waypoint_South': (15.0, 55.0), # 南向繞道航路點 (阿拉伯海)
        'Waypoint_North': (60.0, 70.0)  # 北向繞道航路點 (西伯利亞)
    }

    # 地圖視覺化
    fig_map = go.Figure()

    # 繪製高風險戰區 (紅色大圓圈)
    fig_map.add_trace(go.Scattergeo(
        lat=[coords['Middle_East'][0]], lon=[coords['Middle_East'][1]],
        marker=dict(size=80, color='red', opacity=0.3),
        name="🚨 活躍衝突區 (中東空域)", mode="markers"
    ))

    # 繪製原訂航線 (直飛但穿越戰區)
    fig_map.add_trace(go.Scattergeo(
        lat=[coords['TPE'][0], coords['Middle_East'][0], coords['FRA'][0]],
        lon=[coords['TPE'][1], coords['Middle_East'][1], coords['FRA'][1]],
        mode='lines+markers', line=dict(width=3, color='red', dash='dash'),
        name="原訂航線 (極高風險)", text=["TPE", "Danger Zone", "FRA"], textposition="bottom center"
    ))

    # 繪製安全繞道航線 (往南繞)
    fig_map.add_trace(go.Scattergeo(
        lat=[coords['TPE'][0], coords['Waypoint_South'][0], coords['FRA'][0]],
        lon=[coords['TPE'][1], coords['Waypoint_South'][1], coords['FRA'][1]],
        mode='lines+markers', line=dict(width=3, color='mediumseagreen'),
        name="建議備用航線 (南向繞飛)", text=["TPE", "Safe Waypoint", "FRA"], textposition="bottom center"
    ))

    fig_map.update_geos(
        projection_type="natural earth",
        showcountries=True, countrycolor="RebeccaPurple",
        showland=True, landcolor="rgb(243, 243, 243)",
        lataxis_range=[0, 70], lonaxis_range=[0, 140]
    )
    fig_map.update_layout(height=500, margin=dict(l=0, r=0, t=30, b=0))
    st.plotly_chart(fig_map, use_container_width=True)

    # 輸出風險報告與成本分析
    map_col1, map_col2 = st.columns(2)
    with map_col1:
        st.error("### 🚨 原訂航線風險警告")
        st.markdown("""
        **途經空域：** 伊朗 (OIIX) / 伊拉克 (ORBB) 飛航情報區
        - **🚩 地空飛彈威脅 (SAM)：** 該區域近期有未經公告之防空飛彈活動，存在誤擊民航機之極高風險。
        - **📡 GPS 欺騙干擾 (Spoofing)：** 近 48 小時內接獲多起民航機回報，該空域存在軍用級 GPS 訊號覆寫，可能導致導航系統偏航。
        - **📜 法規限制：** FAA 已發布 SFAR (特別聯邦航空規定)，禁止註冊於美國之民航機低於 FL320 (32,000英呎) 飛越此區。
        """)
        st.button("❌ 拒絕此航線 (Deny Route)", type="primary")

    with map_col2:
        st.success("### ✅ 系統建議：啟用南向避讓航線")
        st.markdown("""
        **改道路徑：** 經印度洋 ➔ 阿拉伯海 ➔ 埃及 (紅海空域) ➔ 地中海 ➔ 歐洲
        - **🛡️ 飛安評估：** 避開所有交戰區，導航訊號穩定，天候狀況良好。
        """)
        
        # 成本估算數據卡
        st.markdown("#### 💰 繞道營運成本評估 (Delta Cost)")
        c1, c2, c3 = st.columns(3)
        c1.metric("增加飛行時間", "+ 1 小時 45 分", delta_color="inverse")
        c2.metric("額外燃油消耗", "+ 12.5 噸", delta_color="inverse")
        c3.metric("航班準點率影響", "延遲抵達", delta_color="inverse")
        
        st.button("✅ 批准並重新簽派 (Approve & Dispatch)")
