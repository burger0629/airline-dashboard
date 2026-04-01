import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from math import pi
import matplotlib

# 設定中文字型與版面
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei'] 
plt.rcParams['axes.unicode_minus'] = False
st.set_page_config(page_title="航空公司營運診斷系統", layout="wide")

# ==========================================
# 網頁標題與側邊欄 (輸入區)
# ==========================================
st.title("✈️ 航空公司年度營運診斷與資源最佳化系統")
st.markdown("透過數據驅動決策，將有限的預算精準投入於飛安與營運缺口。")

st.sidebar.header("📊 請輸入本年度營運指標")
st.sidebar.markdown("請透過滑桿調整各項分數 (0-100分)")

score_safety = st.sidebar.slider("1. 飛安綜合風險控管分數", 0.0, 100.0, 70.0)
score_maintenance = st.sidebar.slider("2. 機隊妥善與維修量能分數", 0.0, 100.0, 65.0)
score_otp = st.sidebar.slider("3. 航班準點率 (OTP) 分數", 0.0, 100.0, 85.0)
score_service = st.sidebar.slider("4. 旅客服務滿意度分數", 0.0, 100.0, 90.0)

st.sidebar.divider()
total_budget_millions = st.sidebar.number_input("💰 系統可用總預算 (百萬台幣)", min_value=10.0, max_value=5000.0, value=500.0, step=10.0)

# ==========================================
# 核心演算法：最佳化資源分配
# ==========================================
weights = {'飛安控管': 0.40, '機隊維修': 0.30, '航班調度': 0.20, '旅客服務': 0.10}
scores = {'飛安控管': score_safety, '機隊維修': score_maintenance, '航班調度': score_otp, '旅客服務': score_service}

target_score = 100.0
urgency_scores = {}
total_urgency = 0

for category in scores:
    gap = max(target_score - scores[category], 1.0) 
    urgency = gap * weights[category]
    urgency_scores[category] = urgency
    total_urgency += urgency

allocations = {}
for category in urgency_scores:
    ratio = urgency_scores[category] / total_urgency
    allocations[category] = total_budget_millions * ratio

# ==========================================
# 網頁主畫面呈現 (輸出區)
# ==========================================
col1, col2 = st.columns(2)

# 左側：雷達圖
with col1:
    st.subheader("營運健康診斷雷達圖")
    categories = list(scores.keys())
    values = list(scores.values())
    values += values[:1]
    N = len(categories)
    angles = [n / float(N) * 2 * pi for n in range(N)]
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    plt.xticks(angles[:-1], categories, size=12, fontweight='bold')
    ax.set_rlabel_position(0)
    plt.yticks([20, 40, 60, 80, 100], ["20", "40", "60", "80", "100"], color="grey", size=10)
    plt.ylim(0, 100)

    ax.plot(angles, values, linewidth=2, linestyle='solid', color='blue', label='當前營運體質')
    ax.fill(angles, values, 'blue', alpha=0.2)
    target_values = [100] * N + [100]
    ax.plot(angles, target_values, linewidth=1.5, linestyle='--', color='green', label='目標最佳化狀態')
    plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
    
    # 將 matplotlib 的圖表顯示在網頁上
    st.pyplot(fig)

# 右側：財務分配與決策建議
with col2:
    st.subheader("💡 最佳化預算分配建議")
    st.info(f"**本年度總預算： {total_budget_millions:,.1f} 百萬台幣**")
    
    # 用迴圈印出每個項目的分配金額
    for category in scores:
        st.metric(label=f"{category} (當前 {scores[category]:.1f} 分)", 
                  value=f"{allocations[category]:.1f} 百萬")

    st.divider()
    st.subheader("⚠️ 系統警示與排程建議")
    max_budget_category = max(allocations, key=allocations.get)
    st.warning(f"最大營運缺口落在 **【{max_budget_category}】**，系統已自動將最大宗資源排程至此項目。")
    
    if score_safety < 80:
        st.error("🚨 **飛安警報**：飛安控管分數低於 80 分，處於高風險狀態。請務必優先執行飛安預算配置，並啟動 SMS 專案審查。")
    else:
        st.success("✅ 飛安指標處於穩定水準。")