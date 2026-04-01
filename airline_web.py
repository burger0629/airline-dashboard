import streamlit as st
import numpy as np
import plotly.graph_objects as go

# 設定網頁版面 (寬版)
st.set_page_config(page_title="航空公司營運診斷系統", layout="wide")

st.title("✈️ 航空公司年度營運診斷與趨勢最佳化系統")
st.markdown("本系統已整合 **年度歷史對比功能** 與 **深度專家診斷知識庫 (Root Cause Analysis)**。")

# ==========================================
# 網頁側邊欄 (數據輸入區)
# ==========================================
st.sidebar.header("📅 營運指標數據輸入")

st.sidebar.subheader("【本年度 (Current Year)】")
curr_safety = st.sidebar.slider("1. 飛安控管 (今年)", 0.0, 100.0, 75.0)
curr_maint = st.sidebar.slider("2. 機隊維修 (今年)", 0.0, 100.0, 65.0)
curr_otp = st.sidebar.slider("3. 航班調度 (今年)", 0.0, 100.0, 85.0)
curr_service = st.sidebar.slider("4. 旅客服務 (今年)", 0.0, 100.0, 90.0)

st.sidebar.divider()

st.sidebar.subheader("【前年度 (Last Year)】")
prev_safety = st.sidebar.slider("1. 飛安控管 (去年)", 0.0, 100.0, 85.0)
prev_maint = st.sidebar.slider("2. 機隊維修 (去年)", 0.0, 100.0, 60.0)
prev_otp = st.sidebar.slider("3. 航班調度 (去年)", 0.0, 100.0, 80.0)
prev_service = st.sidebar.slider("4. 旅客服務 (去年)", 0.0, 100.0, 95.0)

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
# 視覺化呈現：雙雷達圖與財務分配
# ==========================================
col1, col2 = st.columns(2)

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

    # 目標線
    fig.add_trace(go.Scatterpolar(
        r=[100, 100, 100, 100, 100],
        theta=categories + [categories[0]],
        name='目標最佳化狀態',
        line=dict(color='mediumseagreen', dash='dash')
    ))

    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=True,
        margin=dict(l=40, r=40, t=30, b=30)
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("📈 年度指標進退步分析 (YOY)")
    st.info(f"**年度總可用預算： {total_budget:,.1f} 百萬**")
    
    m_cols = st.columns(2)
    for i, cat in enumerate(categories):
        delta = curr_scores[i] - prev_scores[i]
        with m_cols[i % 2]:
            st.metric(label=cat, value=f"{curr_scores[i]:.1f} 分", delta=f"{delta:.1f} 分")
            st.caption(f"💰 建議配置預算: **{allocations[cat]:.1f} 萬**")
            st.write("---")

# ==========================================
# 🛠️ 深度專家知識庫 (Knowledge Base)
# ==========================================
knowledge_base = {
    '飛安控管': {
        'critical': {
            'reasons': ["組織內部存在嚴重的「孤島效應 (Silo Effect)」，各部門飛安數據無法橫向整合。", "防禦機制出現多重失效，形成典型的「瑞士起司理論 (Swiss Cheese Model)」穿透風險。"],
            'actions': ["**[立即停損]** 暫停高風險航線，啟動全機隊無預警安全停飛檢查 (Safety Stand-down)。", "**[外部介入]** 邀請第三方飛安組織進行深度稽核，全面盤點 SMS 漏洞。"]
        },
        'warning': {
            'reasons': ["第一線空勤組員面臨潛在的疲勞累積，情境警覺 (Situational Awareness) 下降。", "輕微異常事件 (Incidents) 通報率下降，基層對「公正文化 (Just Culture)」失去信任。"],
            'actions': ["**[數據監控]** 擴大飛行數據監測 (FOQA) 涵蓋率，設定更嚴格的自動警報門檻。", "**[疲勞管理]** 嚴格檢視疲勞風險管理系統 (FRMS)，利用科學數據重新評估連續派飛的合理性。"]
        },
        'safe': {
            'reasons': ["各項飛安防禦機制運作良好，數據監控與人員訓練均達標。"],
            'actions': ["**[文化深耕]** 持續發放飛安通報獎金，穩固基層的自願通報文化。"]
        }
    },
    '機隊維修': {
        'critical': {
            'reasons': ["維修排程過度緊湊導致嚴重「人為因素 (Human Factors)」失誤，人員為趕工忽略 SOP。", "關鍵航材發生系統性斷鏈，導致機隊長期處於「缺件待料 (AOG)」。"],
            'actions': ["**[立即處置]** 針對妥善率極差的機型強制執行適航指令 (AD) 檢查，風險排除前無限期停飛。", "**[預算挹注]** 立即動用預算採購備用發動機與高消耗性航材，重建安全庫存量。"]
        },
        'warning': {
            'reasons': ["維修廠區溝通瑕疵，早晚班交接時發生資訊遺漏。", "機隊老化，航電系統非預期故障率緩步上升。"],
            'actions': ["**[防護機制]** 導入人為因素視覺化防呆機制，強制落實雙重檢查 (Dual Inspection)。", "**[預防性維護]** 主動將高頻率故障的關鍵零組件，其預防更換週期縮短 15%。"]
        },
        'safe': {
            'reasons': ["機隊妥善率穩定維持在高檔，供應鏈健康。"],
            'actions': ["**[前瞻佈局]** 開始建立 AI 預測性維修 (Predictive Maintenance) 模型，預判零件壽命。"]
        }
    },
    '航班調度': {
        'critical': {
            'reasons': ["未運用作業研究 (OR) 進行資源最佳化，機隊運用與組員派飛嚴重錯配。", "時刻表毫無抗壓性，面對雷雨季缺乏足夠緩衝裕度 (Buffer Time)。"],
            'actions': ["**[立即處置]** 大刀闊斧砍減『紙上航班』，發布符合真實運能的保守版時刻表。", "**[節點控管]** 暫緩經常性塞機樞紐機場的新航權與起降時帶 (Slot) 申請。"]
        },
        'warning': {
            'reasons': ["機場地停作業 (Turnaround) 效率不彰，各環節未能緊密銜接。", "簽派、機務與地勤之間的資訊傳遞存在時間差。"],
            'actions': ["**[效率優化]** 重新精算並壓縮關鍵路徑 (Critical Path) 上的閒置時間。", "**[協同決策]** 建立 A-CDM (機場協同決策) 數據連線，提前預判流量管制。"]
        },
        'safe': {
            'reasons': ["準點率高於業界標準，抗壓性良好。"],
            'actions': ["**[精益管理]** 針對特定長程航班進行飛行計畫 (Flight Plan) 的燃油經濟性最佳化。"]
        }
    },
    '旅客服務': {
        'critical': {
            'reasons': ["第一線人員對異常航班 (IRROPS) 處理 SOP 模糊，導致旅客面對資訊黑洞。", "外包地勤或餐飲供應商履約品質低劣，拖累品牌形象。"],
            'actions': ["**[流程再造]** 重新修訂班機延誤補償 SOP，大幅下放前線主管決策權限。", "**[供應商管理]** 若第三方代理商下個月 KPI 未達標，立即啟動解約程序。"]
        },
        'warning': {
            'reasons': ["數位化服務落後，APP 在航班大亂時無法乘載流量，推播通知慢半拍。", "第一線員工面對不理性旅客缺乏危機溝通訓練。"],
            'actions': ["**[資訊透明]** 強制升級 APP 伺服器，確保航班異動能在 5 分鐘內主動推播至旅客手機。", "**[根因分析]** 導入文字探勘技術分析客訴信件，找出導致不滿的核心關鍵字。"]
        },
        'safe': {
            'reasons': ["旅客滿意度維持高檔，服務流程順暢。"],
            'actions': ["**[價值提升]** 將資源投入常客忠誠度計畫 (FFP)，提升高收益商務客回流率。"]
        }
    }
}

# ==========================================
# 🛠️ 自訂 UI 渲染元件與動態邏輯
# ==========================================
st.divider()
st.subheader("📋 趨勢診斷與深度改善行動書")

for i, cat in enumerate(categories):
    curr_score = curr_scores[i]
    prev_score = prev_scores[i]
    delta = curr_score - prev_score
    
    # 風險等級判定
    if curr_score < 60:
        level, bg_color, border_color, text_color, icon, status_text = ('critical', "#fff0f0", "#ff4b4b", "#900000", "🚨", "非常嚴重 (CRITICAL)")
        if st.get_option("theme.base") == "dark": bg_color, text_color = "#3a0000", "#ff4b4b"
    elif curr_score < 80:
        level, bg_color, border_color, text_color, icon, status_text = ('warning', "#fffbe6", "#ffc107", "#856404", "⚠️", "危險警告 (WARNING)")
        if st.get_option("theme.base") == "dark": bg_color, text_color = "#332b00", "#ffc107"
    else:
        level, bg_color, border_color, text_color, icon, status_text = ('safe', "#f0fff4", "#28a745", "#155724", "✅", "安全穩定 (SAFE)")
        if st.get_option("theme.base") == "dark": bg_color, text_color = "#002b12", "#28a745"

    # 動態趨勢評語
    if delta >= 5:
        trend_label = f"📈 顯著進步 (+{delta:.1f})"
        trend_desc = "已較去年顯著進步，防禦與管理機制奏效，請持續保持優化力道。"
    elif delta <= -5:
        trend_label = f"📉 嚴重衰退 ({delta:.1f})"
        trend_desc = "較去年嚴重衰退！需徹查資源是否斷鏈、管理是否出現真空或 SOP 未落實。"
    else:
        trend_label = f"➖ 表現持平 ({delta:+.1f})"
        trend_desc = "與去年相比無顯著變動。若處於危險區間，代表現有資源投入缺乏效用，需改變策略。"

    # 渲染專屬卡片
    st.markdown(f"""
    <div style="background-color:{bg_color}; padding:20px; border-radius:10px; border-left: 10px solid {border_color}; margin-top: 20px; margin-bottom: 10px;">
        <h3 style="color:{text_color}; margin-top:0;">{icon} {cat} | 本年得分：{curr_score:.1f} ({trend_label})</h3>
        <p style="color:{text_color}; font-weight:bold; font-size: 1.1em; margin-bottom: 5px;">狀態判定：{status_text}</p>
        <p style="color:{text_color}; font-size: 0.95em; margin-bottom: 0;"><b>年度趨勢分析：</b>{trend_desc}</p>
    </div>
    """, unsafe_allow_html=True)

    # 展開詳細的根因分析與行動方案
    data = knowledge_base[cat][level]
    
    # 針對危險與嚴重的類別，才顯示潛在原因
    if level in ['critical', 'warning']:
        st.markdown(f"#### 🔍 潛在根本原因 (Root Cause)")
        for reason in data['reasons']:
            st.markdown(f"- 🚩 {reason}")
    
    st.markdown(f"#### 🛠️ 具體執行方案 (Action Plan)")
    for action in data['actions']:
        st.markdown(f"- {action}")
    
    st.markdown("<br>", unsafe_allow_html=True)
