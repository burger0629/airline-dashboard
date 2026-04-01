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
st.markdown("整合 **六級風險診斷**、**作業研究最佳化**、**長期趨勢預測** 與 **動態沙盤推演** 的決策支援系統。")

# ==========================================
# 網頁側邊欄 (數據輸入與報告匯出)
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
# 優化一：作業研究線性/非線性最佳化 (LP/NLP Allocation)
# ==========================================
# 目標函數：最小化「距離100分的缺口加權總和」 (等同最大化健康度)
# 假設投入預算 x，分數提升符合邊際效益遞減：new_score = current_score + k * sqrt(x)
def objective(x, current_scores, weights):
    k_factors = np.array([1.5, 2.0, 1.2, 1.0]) # 各部門預算轉換分數的效率參數
    new_scores = current_scores + k_factors * np.sqrt(x)
    new_scores = np.clip(new_scores, 0, 100)
    gaps = 100 - new_scores
    return np.sum(weights * gaps)

# 限制條件：總預算不超過 total_budget，且每個部門至少獲得 2% 基本維運費
constraints = {'type': 'eq', 'fun': lambda x: np.sum(x) - total_budget}
bounds = tuple((total_budget * 0.02, total_budget) for _ in range(4))
initial_guess = np.array([total_budget/4]*4)

result = minimize(objective, initial_guess, args=(curr_scores, weights), method='SLSQP', bounds=bounds, constraints=constraints)
allocations = result.x if result.success else initial_guess
alloc_dict = {cat: alloc for cat, alloc in zip(categories, allocations)}

# ==========================================
# 優化四：一鍵匯出營運診斷書 (Markdown 報告)
# ==========================================
report_content = f"""# 航空公司年度營運診斷與資源最佳化報告
**報告生成時間：** {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**總可用預算：** {total_budget} 百萬台幣

## 一、 年度指標進退步分析
"""
for i, cat in enumerate(categories):
    delta = curr_scores[i] - prev_scores[i]
    report_content += f"- **{cat}**：本年 {curr_scores[i]:.1f} 分 (去年 {prev_scores[i]:.1f} 分) | 變動：{delta:+.1f} 分\n"

report_content += "\n## 二、 最佳化預算配置建議 (基於限制最佳化模型)\n"
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
# 建立頁籤架構 (Tabs)
# ==========================================
tab1, tab2, tab3 = st.tabs(["📊 核心診斷與最佳化分配", "📈 長期趨勢與數據匯入", "🔮 What-If 沙盤推演"])

with tab1:
    # (此處保留原本的雙雷達圖與專家知識庫卡片)
    col1, col2 = st.columns([1.2, 1])
    with col1:
        st.subheader("🔄 年度營運體質對比雷達圖")
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(r=list(prev_scores)+[prev_scores[0]], theta=categories+[categories[0]], fill='toself', name='前年度', line_color='rgba(150, 150, 150, 0.5)'))
        fig.add_trace(go.Scatterpolar(r=list(curr_scores)+[curr_scores[0]], theta=categories+[categories[0]], fill='toself', name='本年度', line_color='royalblue', fillcolor='rgba(65, 105, 225, 0.2)'))
        fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), margin=dict(l=40, r=40, t=30, b=30))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("數學模型最佳化預算分配")
        st.info("系統已運用 **SLSQP 演算法** 求解預算限制式，算出最大化整體分數的最佳解。")
        m_cols = st.columns(2)
        for i, cat in enumerate(categories):
            delta = curr_scores[i] - prev_scores[i]
            with m_cols[i % 2]:
                st.metric(label=cat, value=f"{curr_scores[i]:.1f} 分", delta=f"{delta:.1f} 分")
                st.caption(f"💰 建議最佳化預算: **{alloc_dict[cat]:.1f} 百萬**")

    # 專家診斷模組 (簡化版呈現)
    st.divider()
    st.subheader("📋 系統自動化專家診斷")
    for i, cat in enumerate(categories):
        score = curr_scores[i]
        if score < 60:
            st.error(f"🚨 **{cat} (非常嚴重)**：存在組織性漏洞。建議：立即成立專案小組，啟動強制性稽核，並暫停高風險運作。")
        elif score < 80:
            st.warning(f"⚠️ **{cat} (危險警告)**：防護網出現破口。建議：擴大數據監控 (如 FOQA)，並強化前線人員之 SOP 落實度。")
        else:
            st.success(f"✅ **{cat} (安全穩定)**：運作健康。建議：維持現有資源配置，推動公正文化 (Just Culture)。")

with tab2:
    # ==========================================
    # 優化三：長期趨勢與檔案分析
    # ==========================================
    st.subheader("📈 歷史營運數據趨勢分析 (五年期)")
    st.markdown("您可以上傳包含歷史數據的 CSV 檔案，或查看系統預設的模擬數據。")
    
    uploaded_file = st.file_uploader("📂 上傳歷史營運數據 (CSV)", type="csv")
    
    if uploaded_file is not None:
        df_trend = pd.read_csv(uploaded_file)
        st.success("檔案讀取成功！")
    else:
        # 生成預設的五年模擬數據
        years = ['2022', '2023', '2024', '2025', '2026(YTD)']
        df_trend = pd.DataFrame({
            '年份': years,
            '飛安控管': [92, 88, 85, prev_safety, curr_safety],
            '機隊維修': [80, 75, 65, prev_maint, curr_maint],
            '航班調度': [88, 85, 82, prev_otp, curr_otp],
            '旅客服務': [85, 90, 92, prev_service, curr_service]
        })
    
    # 使用 Plotly 繪製互動式折線圖
    df_melted = df_trend.melt(id_vars=['年份'], var_name='營運指標', value_name='分數')
    fig_line = px.line(df_melted, x='年份', y='分數', color='營運指標', markers=True, title='各項營運指標長期趨勢追蹤')
    fig_line.update_layout(yaxis=dict(range=[0, 100]))
    st.plotly_chart(fig_line, use_container_width=True)
    
    with st.expander("📄 查看詳細數據表格"):
        st.dataframe(df_trend, use_container_width=True)

with tab3:
    # ==========================================
    # 優化二：What-If 預測沙盤推演
    # ==========================================
    st.subheader("🔮 決策沙盤推演 (What-If Simulator)")
    st.markdown("若不採用系統的最佳化建議，您可以手動調配明年的預算。系統將利用預測模型，**反向推算明年度的預期營運分數**。")
    
    st.info(f"您目前共有 **{total_budget} 百萬** 的籌碼可以分配。")
    
    sim_cols = st.columns(4)
    sim_allocs = []
    
    # 讓使用者手動輸入模擬預算
    for i, cat in enumerate(categories):
        with sim_cols[i]:
            val = st.number_input(f"投入【{cat}】(百萬)", min_value=0.0, max_value=float(total_budget), value=float(alloc_dict[cat]), step=10.0)
            sim_allocs.append(val)
            
    total_sim = sum(sim_allocs)
    
    if total_sim > total_budget:
        st.error(f"⚠️ 預算超支！您分配了 {total_sim} 百萬，但總預算只有 {total_budget} 百萬。")
    else:
        st.success(f"預算分配完畢 (剩餘 {total_budget - total_sim} 百萬)。以下為系統預測之明年成績：")
        
        # 預測運算邏輯 (邊際效益遞減模型)
        k_factors = np.array([1.5, 2.0, 1.2, 1.0])
        predicted_scores = curr_scores + k_factors * np.sqrt(sim_allocs)
        predicted_scores = np.clip(predicted_scores, 0, 100)
        
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
