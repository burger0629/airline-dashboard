import streamlit as st
import numpy as np
import plotly.graph_objects as go

# 設定網頁版面 (寬版)
st.set_page_config(page_title="航空公司營運診斷系統", layout="wide")

st.title("✈️ 航空公司年度營運診斷與資源最佳化系統")
st.markdown("系統已啟用三級風險管理機制，並導入 **根因分析 (Root Cause Analysis)** 與 **深度行動方案**。")

# ==========================================
# 網頁側邊欄 (輸入區)
# ==========================================
st.sidebar.header("📊 營運指標數據輸入")
score_safety = st.sidebar.slider("1. 飛安綜合風險控管分數", 0.0, 100.0, 55.0)
score_maintenance = st.sidebar.slider("2. 機隊妥善與維修量能分數", 0.0, 100.0, 65.0)
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
# 🛠️ 自訂 UI 元件：深度診斷卡片
# ==========================================
def render_diagnosis_card(category, score, level, data):
    if level == 'critical':
        bg_color, border_color, text_color, icon, status_text = ("#3a0000" if st.get_option("theme.base") == "dark" else "#fff0f0", "#ff4b4b", "#ff4b4b" if st.get_option("theme.base") == "dark" else "#900000", "🚨", "非常嚴重 (CRITICAL)")
    elif level == 'warning':
        bg_color, border_color, text_color, icon, status_text = ("#332b00" if st.get_option("theme.base") == "dark" else "#fffbe6", "#ffc107", "#ffc107" if st.get_option("theme.base") == "dark" else "#856404", "⚠️", "危險警告 (WARNING)")
    else:
        bg_color, border_color, text_color, icon, status_text = ("#002b12" if st.get_option("theme.base") == "dark" else "#f0fff4", "#28a745", "#28a745" if st.get_option("theme.base") == "dark" else "#155724", "✅", "安全穩定 (SAFE)")

    st.markdown(f"""
    <div style="background-color:{bg_color}; padding:20px; border-radius:10px; border-left: 10px solid {border_color}; margin-top: 20px; margin-bottom: 15px;">
        <h3 style="color:{text_color}; margin-top:0;">{icon} {category} | 系統評估得分：<span style="font-size: 1.3em;">{score:.1f}</span> / 100</h3>
        <p style="color:{text_color}; font-weight:bold; font-size: 1.1em;">狀態判定：{status_text}</p>
    </div>
    """, unsafe_allow_html=True)

    # 渲染根本原因 (只在非安全狀態顯示)
    if level in ['critical', 'warning']:
        st.markdown(f"#### 🔍 潛在根本原因分析 (Root Cause Analysis)")
        for reason in data['reasons']:
            st.markdown(f"- 🚩 {reason}")
        st.markdown("---")

    # 渲染具體行動方案
    st.markdown(f"#### 🛠️ 具體執行方案 (Detailed Action Plan)")
    for action in data['actions']:
        st.markdown(f"- {action}")
    st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# 🛠️ 深度專業知識庫 (含根因與具體作為)
# ==========================================
st.divider()
st.subheader("📋 各領域專案深度改善行動書")

knowledge_base = {
    '飛安控管': {
        'critical': {
            'reasons': [
                "組織內部可能存在嚴重的「孤島效應 (Silo Effect)」，導致機務、航務與簽派部門的飛安數據無法有效橫向整合。",
                "防禦機制出現多重失效，各項安全檢核點流於形式，形成典型的「瑞士起司理論 (Swiss Cheese Model)」穿透風險。",
                "安全管理系統 (SMS) 失去主動預測功能，退化為僅能事後檢討的被動機制。"
            ],
            'actions': [
                "**[立即停損]** 立即暫停易受天候與地形干擾之高風險航線，並啟動全機隊無預警安全停飛檢查 (Safety Stand-down)。", 
                "**[打破孤島]** 成立由總經理直屬的跨部門緊急應變小組 (Task Force)，強制打通飛航數據與維修紀錄的資料壁壘。", 
                "**[外部介入]** 邀請民航局或國際第三方飛安組織，進行為期兩週的深度專案稽核，全面盤點 SMS 漏洞。"
            ]
        },
        'warning': {
            'reasons': [
                "第一線空勤組員面臨潛在的疲勞累積，導致情境警覺 (Situational Awareness) 下降。",
                "近期的輕微異常事件 (Incidents) 通報率異常下降，顯示基層可能對公司的「公正文化 (Just Culture)」失去信任。"
            ],
            'actions': [
                "**[數據監控]** 擴大飛行數據監測 (FOQA) 涵蓋率，針對重落地、超速等偏差行為設定更嚴格的自動警報門檻。", 
                "**[防護機制]** 嚴格檢視疲勞風險管理系統 (FRMS)，利用科學數據重新評估紅眼航班與連續派飛的合理性。",
                "**[教育訓練]** 針對所有正副機師辦理「組員資源管理 (CRM)」複訓，強化駕駛艙內的溝通與質疑權威能力。"
            ]
        },
        'safe': {
            'reasons': ["各項飛安防禦機制運作良好，數據監控與人員訓練均達標。"],
            'actions': [
                "**[文化深耕]** 持續發放飛安通報獎金，穩固基層的自願通報文化。", 
                "**[壓力測試]** 策劃高強度的年度無預警重大空難演習，維持組織面對極端事件的肌肉記憶。"
            ]
        }
    },
    '機隊維修': {
        'critical': {
            'reasons': [
                "維修排程過度緊湊，導致嚴重「人為因素 (Human Factors)」失誤，維修人員為趕工而選擇性忽略標準作業程序 (SOP)。",
                "關鍵航材供應鏈發生系統性斷鏈，導致機隊長期處於「缺件待料 (AOG)」的窘境。",
                "缺乏妥善的預防性維護計畫，多數維修轉為高成本且高風險的「故障後維修」。"
            ],
            'actions': [
                "**[立即處置]** 針對妥善率極差的特定機型，強制執行適航指令 (AD) 深度檢查，風險無法排除前無限期停飛。", 
                "**[流程重整]** 重新審定維修工時標準，嚴格取締任何形式的『捷徑行為 (Workarounds)』，並重新考核關鍵技術人員。", 
                "**[預算挹注]** 立即動用緊急預算採購備用發動機與高消耗性航材，重建安全庫存量 (Safety Stock)。"
            ]
        },
        'warning': {
            'reasons': [
                "維修廠區的溝通與交接流程存在瑕疵，容易在早晚班交接時發生資訊遺漏。",
                "機隊逐漸老化，部分航電系統的非預期故障率開始呈現緩步上升趨勢。"
            ],
            'actions': [
                "**[防護機制]** 於維修廠區全面導入人為因素視覺化防呆機制，強制落實工具清點與雙重檢查 (Dual Inspection)。", 
                "**[數位轉型]** 加速淘汰紙本工單，全面落實數位化維修追蹤，確保每一個螺絲的更換都有數位簽章可循。",
                "**[預防性維護]** 主動將高頻率故障的關鍵零組件，其預防性更換週期縮短 15%。"
            ]
        },
        'safe': {
            'reasons': ["維修量能充沛，機隊妥善率穩定維持在高檔，供應鏈健康。"],
            'actions': [
                "**[持續維運]** 確實執行各機隊之例行 A、B、C、D 檢。", 
                "**[前瞻佈局]** 運用結餘預算，開始建立 AI 預測性維修 (Predictive Maintenance) 模型，分析感測器數據以預判零件壽命。"
            ]
        }
    },
    '航班調度': {
        'critical': {
            'reasons': [
                "航班排程未運用線性規劃等科學方法進行資源最佳化，導致機隊運用與空勤組員派飛嚴重錯配。",
                "時刻表排定過於理想化，毫無抗壓性，面對雷雨季或突發航管流量管制時，缺乏足夠的緩衝裕度 (Buffer Time)。"
            ],
            'actions': [
                "**[立即處置]** 大刀闊斧砍減延誤率常態性超過 40% 的『紙上航班』，重新發布符合真實運能的保守版時刻表。", 
                "**[資源重配]** 利用作業研究 (Operations Research) 模型，重新計算並補足備用機 (Spare Aircraft) 與待命組員 (Standby) 的真實缺口。", 
                "**[節點控管]** 針對經常性塞機的樞紐機場，全面暫緩新航權與起降時帶 (Slot) 的擴張申請。"
            ]
        },
        'warning': {
            'reasons': [
                "機場地停作業 (Turnaround) 效率不彰，清潔、上餐、加油等環節未能緊密銜接。",
                "跨部門協調不足，簽派、機務與地勤之間的資訊傳遞存在時間差。"
            ],
            'actions': [
                "**[效率優化]** 重新繪製地停作業的甘特圖，精算並壓縮關鍵路徑 (Critical Path) 上的閒置時間。", 
                "**[協同決策]** 建立與當地氣象局、航管單位的 A-CDM (機場協同決策) 數據連線，提前預判流量管制並動態調度。",
                "**[航網微調]** 將容易受氣候影響的航班，策略性地調移至非尖峰時段。"
            ]
        },
        'safe': {
            'reasons': ["準點率高於業界標準，備用資源配置合理，抗壓性良好。"],
            'actions': [
                "**[精益管理]** 在確保高準點率的前提下，針對特定長程航班進行飛行計畫 (Flight Plan) 的燃油經濟性最佳化。",
                "**[持續維運]** 維持現有的動態班表調度機制。"
            ]
        }
    },
    '旅客服務': {
        'critical': {
            'reasons': [
                "第一線人員對於異常航班 (IRROPS) 的處理 SOP 充滿模糊地帶，導致旅客面對無止盡的等待與資訊黑洞。",
                "外包的地勤代理商或餐飲供應商履約品質低劣，嚴重拖累公司整體品牌形象。"
            ],
            'actions': [
                "**[立即處置]** 針對社群網路上負評炸鍋的服務斷點，立即啟動高層級的服務補救專案 (Service Recovery)。", 
                "**[流程再造]** 重新修訂班機延誤/取消的旅客安置與現金補償 SOP，並大幅下放前線主管的決策權限。", 
                "**[供應商管理]** 發出最後通牒，若第三方地勤代理商下個月 KPI 未達標，立即啟動解約與替換程序。"
            ]
        },
        'warning': {
            'reasons': [
                "數位化服務落後，官網或 APP 在航班大亂時無法乘載流量，且推播通知往往慢半拍。",
                "第一線員工面對不理性旅客時，缺乏足夠的危機溝通與情緒管理訓練。"
            ],
            'actions': [
                "**[前線賦能]** 增加地勤與空服人員針對『奧客衝突與安撫』的實境模擬訓練，增強抗壓性。", 
                "**[資訊透明]** 強制升級 APP 伺服器乘載力，確保航班異動能在 5 分鐘內主動推播至旅客手機，降低不確定感。", 
                "**[根因分析]** 導入文字探勘技術分析客服客訴信件，精準找出導致旅客不滿的核心關鍵字。"
            ]
        },
        'safe': {
            'reasons': ["旅客滿意度維持高檔，第一線服務流程順暢且具備溫度。"],
            'actions': [
                "**[價值提升]** 將服務資源向金字塔頂端傾斜，優化常客忠誠度計畫 (FFP) 的個人化專屬體驗。",
                "**[持續優化]** 定期進行神秘客 (Mystery Shopper) 抽查，確保各外站服務品質一致。"
            ]
        }
    }
}

for cat, score in scores.items():
    if score < 60:
        render_diagnosis_card(cat, score, 'critical', knowledge_base[cat]['critical'])
    elif score < 80:
        render_diagnosis_card(cat, score, 'warning', knowledge_base[cat]['warning'])
    else:
        render_diagnosis_card(cat, score, 'safe', knowledge_base[cat]['safe'])
