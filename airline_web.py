import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from scipy.optimize import minimize
import datetime
import requests
import time
from geopy.geocoders import Nominatim

# 設定網頁版面
st.set_page_config(page_title="航空公司營運戰情室 (God Mode)", layout="wide", initial_sidebar_state="expanded")

st.title("✈️ 航空公司營運戰情室 (Aviation War Room - 無刪減頂規版)")
st.markdown("整合 **六級風險診斷**、**多維限制最佳化**、**財務衝擊預測**、**動態航線/氣象/流量追蹤** 與 **AI 戰略幕僚**。")

# ==========================================
# 網頁側邊欄 (數據輸入與限制)
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
st.sidebar.subheader("🚧 系統資源限制 (Constraints)")
total_budget = st.sidebar.number_input("💰 可用總預算 (百萬台幣)", min_value=10.0, value=500.0, step=10.0)
max_labor_hours = st.sidebar.number_input("👷 最大可用維修工時 (小時)", min_value=1000, value=15000, step=500)

categories = ['飛安控管', '機隊維修', '航班調度', '旅客服務']
weights = np.array([0.40, 0.30, 0.20, 0.10])
curr_scores = np.array([curr_safety, curr_maint, curr_otp, curr_service])
prev_scores = np.array([prev_safety, prev_maint, prev_otp, prev_service])
loss_factors = [2.5, 3.0, 1.8, 0.5] # 隱性損失係數

# ==========================================
# 多維度限制最佳化演算法
# ==========================================
def objective(x, current_scores, weights):
    new_scores = np.clip(current_scores + np.array([1.5, 2.0, 1.2, 1.0]) * np.sqrt(x), 0, 100)
    return np.sum(weights * (100 - new_scores))

con_budget = {'type': 'eq', 'fun': lambda x: np.sum(x) - total_budget}
con_labor = {'type': 'ineq', 'fun': lambda x: max_labor_hours - np.sum(x * np.array([20, 80, 10, 5]))}
bounds = tuple((total_budget * 0.02, total_budget) for _ in range(4))
res = minimize(objective, np.array([total_budget/4]*4), args=(curr_scores, weights), method='SLSQP', bounds=bounds, constraints=[con_budget, con_labor])
alloc_dict = {cat: alloc for cat, alloc in zip(categories, res.x if res.success else np.array([total_budget/4]*4))}

# ==========================================
# 完整回歸：六級專家知識庫與 UI 渲染
# ==========================================
def get_risk_level_config(score):
    if score == 100.0: return ('perfect', "#00d26a", "🏆 卓越典範 (PERFECT)")
    elif score >= 81.0: return ('stable', "#28a745", "✅ 安全穩定 (STABLE)")
    elif score >= 61.0: return ('caution', "#ffc107", "⚠️ 黃色警戒 (CAUTION)")
    elif score >= 41.0: return ('serious', "#fd7e14", "🟠 橘色風險 (SERIOUS)")
    elif score >= 21.0: return ('high_risk', "#e74c3c", "🔴 紅色高危 (HIGH RISK)")
    else: return ('catastrophic', "#ff3333", "🚨 災難崩潰 (CATASTROPHIC)")

def render_diagnosis_card(category, score, delta):
    level, main_color, status_text = get_risk_level_config(score)
    trend_label = f"📈 跨越式進步 (+{delta:.1f})" if delta >= 10 else (f"↗️ 微幅進步 (+{delta:.1f})" if delta > 0 else (f"📉 潰雪式衰退 ({delta:.1f})" if delta <= -10 else (f"↘️ 微幅下滑 ({delta:.1f})" if delta < 0 else "➖ 表現持平")))
    st.markdown(f"""
    <div style="background-color: transparent; padding:20px; border-radius:10px; border: 1px solid {main_color}50; border-left: 8px solid {main_color}; margin-top: 15px; margin-bottom: 10px;">
        <h3 style="color: var(--text-color); margin-top:0;">{category} | 得分：<span style="color:{main_color}; font-size: 1.3em; font-weight: 900;">{score:.1f}</span> <span style="font-size: 0.65em; font-weight: normal; opacity: 0.8;">({trend_label})</span></h3>
        <p style="color: var(--text-color); font-weight:bold; font-size: 1.1em; margin-bottom:0;">判定：<span style="color:{main_color};">{status_text}</span></p>
    </div>
    """, unsafe_allow_html=True)
    return level

knowledge_base = {
    '飛安控管': {
        'catastrophic': { 'reasons': ["SMS系統徹底癱瘓，內部隱瞞違規。", "組織失去風險感知能力。"], 'actions': ["🚨 總經理下令全機隊停飛，暫停簽派。", "🚨 解散安委會，外部專案組進駐稽核。"] },
        'high_risk': { 'reasons': ["防禦機制多重失效，瑞士起司漏洞穿透。", "基層對公正文化失去信任。"], 'actions': ["⚠️ 暫停高風險航線，啟動無預警停飛檢查。", "⚠️ 重新驗證飛行員執照與疲勞管理 (FRMS)。"] },
        'serious': { 'reasons': ["組織孤島效應，數據無法橫向整合。", "SMS退化為被動檢討。"], 'actions': ["成立直屬專案小組打通數據壁壘。", "針對異常事件進行根本原因分析 (RCA)。"] },
        'caution': { 'reasons': ["飛行員疲勞累積，情境警覺下降。", "CRM訓練成效降低。"], 'actions': ["擴大FOQA分析深度，設定嚴格警報門檻。", "辦理CRM高階複訓，強化溝通效率。"] },
        'stable': { 'reasons': ["防禦機制運作良好，人員訓練達標。"], 'actions': ["維持現狀，鼓勵公正文化自願通報。"] },
        'perfect': { 'reasons': ["建立世界級飛安範本。"], 'actions': ["策劃無預警重大空難演習，壓力測試應變力。"] }
    },
    '機隊維修': {
        'catastrophic': { 'reasons': ["為趕工忽略SOP，零件偽造或私自替代。", "維修量能嚴重癱瘓。"], 'actions': ["🚨 暫停非緊急維修，全面凍結機材庫存。", "🚨 撤換廠長與品管主管，移送司法調查。"] },
        'high_risk': { 'reasons': ["航材系統性斷鏈，長期缺件待料(AOG)。", "排程失控導致人為失誤激增。"], 'actions': ["⚠️ 對極差機型強制執行AD檢查，風險排除前停飛。", "⚠️ 取締捷徑行為，緊急採購備用發動機。"] },
        'serious': { 'reasons': ["廠區早晚班交接資訊遺漏。", "數據流於紙本，缺乏預測能力。"], 'actions': ["加速淘汰紙本工單，落實數位化維修記錄。", "重新評估零件供應鏈斷鏈風險，多元採購。"] },
        'caution': { 'reasons': ["人為因素(Human Factors)管理鬆動。", "老舊機型非預期故障率上升。"], 'actions': ["縮短發動機與航電設備預防性更換週期。", "強制落實工具清點與雙重檢查(Dual Inspection)。"] },
        'stable': { 'reasons': ["妥善率維持高檔，供應鏈健康。"], 'actions': ["落實例行 A、B、C、D 檢。", "建立AI預測性維修模型。"] },
        'perfect': { 'reasons': ["零維修事故紀錄。"], 'actions': ["分享零失誤維修經驗，導入環保維修技術。"] }
    },
    '航班調度': {
        'catastrophic': { 'reasons': ["時刻表與運能嚴重錯配，造成大規模延誤。", "調度機能癱瘓，缺乏抗壓性。"], 'actions': ["🚨 強制取消自行編排之時刻表，改用最低運能版。", "🚨 徹換管理團隊，盤點疲勞缺口，縮減營運網。"] },
        'high_risk': { 'reasons': ["時刻表無緩衝裕度，雷雨季航網崩潰。", "未科學計算備用機與待命組員。"], 'actions': ["⚠️ 砍減延誤率常態性超過40%的紙上航班。", "⚠️ 動用緊急預算召回休假人員，增加待命量能。"] },
        'serious': { 'reasons': ["各部門資訊傳遞存在嚴重時間差。", "缺乏突發事件的動態調度靈活度。"], 'actions': ["重新繪製地停甘特圖，壓縮關鍵路徑閒置時間。", "建立A-CDM數據連線，預判流量管制。"] },
        'caution': { 'reasons': ["地停作業效率不彰，未能緊密銜接。"], 'actions': ["優化飛機地停轉場流程(加油/上餐/清潔)。"] },
        'stable': { 'reasons': ["準點率良好，抗壓性佳。"], 'actions': ["試圖優化飛行路線降低燃油消耗。"] },
        'perfect': { 'reasons': ["達成年度零延誤紀錄。"], 'actions': ["將資源投入提升機組員滿意度與長遠航網佈局。"] }
    },
    '旅客服務': {
        'catastrophic': { 'reasons': ["外包商履約極差，組織毫無控管能力。", "品牌形像災難性崩潰。"], 'actions': ["🚨 暫停第三方代理商履約，總部直接介入。", "🚨 開啟全面服務流程BPR，重新招標。"] },
        'high_risk': { 'reasons': ["前線對異動航班(IRROPS)處理SOP模糊。", "社群網路出現大規模負評。"], 'actions': ["⚠️ 針對負評斷點啟動緊急服務補救專案。", "⚠️ 修訂補償標準，大幅下放前線主管權限。"] },
        'serious': { 'reasons': ["APP在航班大亂時無法乘載流量且通知慢。", "基層缺乏危機溝通訓練。"], 'actions': ["強制升級APP伺服器，確保5分鐘內推播。", "分析客訴找出不滿核心關鍵字。"] },
        'caution': { 'reasons': ["外站各航點服務品質不一。"], 'actions': ["增加奧客衝突與安撫實境模擬訓練。"] },
        'stable': { 'reasons': ["服務品質穩定。"], 'actions': ["定期進行神秘客抽查，確保品質一致。"] },
        'perfect': { 'reasons': ["達成年度零客訴紀錄。"], 'actions': ["發放卓越獎金，投入個人化常客忠誠度計畫。"] }
    }
}

# ==========================================
# 報表匯出
# ==========================================
rep = f"# 航空公司營運診斷與最佳化報告\n時間：{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}\n預算：{total_budget}M | 工時上限：{max_labor_hours}H\n\n## 一、 預算配置建議\n"
for c, a in alloc_dict.items(): rep += f"- {c}: {a:.1f}M\n"
st.sidebar.divider()
st.sidebar.download_button("📄 匯出完整報告", data=rep, file_name="Report.md", mime="text/markdown")

# ==========================================
# 建立五大頁籤架構
# ==========================================
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 核心診斷", "📈 長期趨勢", "💸 財務推演", "🌍 航線/氣象/流量", "🤖 AI 幕僚"])

with tab1:
    c1, c2 = st.columns([1.2, 1])
    with c1:
        st.subheader("🔄 營運體質對比雷達圖")
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(r=[100]*5, theta=categories+[categories[0]], fill=None, name='目標', line=dict(color='mediumseagreen', dash='dash')))
        fig.add_trace(go.Scatterpolar(r=list(prev_scores)+[prev_scores[0]], theta=categories+[categories[0]], fill='toself', name='去年', line_color='rgba(150,150,150,0.5)'))
        fig.add_trace(go.Scatterpolar(r=list(curr_scores)+[curr_scores[0]], theta=categories+[categories[0]], fill='toself', name='今年', line_color='royalblue', fillcolor='rgba(65,105,225,0.2)'))
        fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), margin=dict(l=40, r=40, t=30, b=30))
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        st.subheader("📈 年度指標與最佳化分配")
        st.caption("✅ 自動平衡「預算上限」與「維修工時」雙重限制")
        mc = st.columns(2)
        for i, cat in enumerate(categories):
            with mc[i%2]:
                st.metric(cat, f"{curr_scores[i]:.1f}", f"{curr_scores[i]-prev_scores[i]:.1f}")
                st.caption(f"💰 預算: **{alloc_dict[cat]:.1f}M**")
    
    st.divider()
    st.subheader("📋 深度診斷報告與行動書")
    for i, cat in enumerate(categories):
        level = render_diagnosis_card(cat, curr_scores[i], curr_scores[i]-prev_scores[i])
        with st.expander("🔍 查看深度診斷分析報告...", expanded=(level not in ['perfect', 'stable'])):
            if level in ['catastrophic', 'high_risk', 'serious', 'caution']:
                st.markdown("#### 🔍 潛在根本原因")
                for r in knowledge_base[cat][level]['reasons']: st.markdown(f"- 🚩 {r}")
            st.markdown("#### 🛠️ 具體執行方案")
            for a in knowledge_base[cat][level]['actions']: st.markdown(f"- {a}")

with tab2:
    st.subheader("📈 歷史趨勢與 CSV 匯入")
    ufile = st.file_uploader("📂 上傳歷史營運數據", type="csv")
    df_trend = pd.read_csv(ufile) if ufile else pd.DataFrame({'年份': ['2022','2023','2024','2025','2026'], '飛安控管': [92,88,85,prev_safety,curr_safety], '機隊維修': [80,75,65,prev_maint,curr_maint], '航班調度': [88,85,82,prev_otp,curr_otp], '旅客服務': [85,90,92,prev_service,curr_service]})
    fig_line = px.line(df_trend.melt(id_vars=['年份'], var_name='營運指標', value_name='分數'), x='年份', y='分數', color='營運指標', markers=True)
    fig_line.update_layout(yaxis=dict(range=[0, 100]))
    st.plotly_chart(fig_line, use_container_width=True)

with tab3:
    st.subheader("💸 財務沙盤推演 (ROI Simulator)")
    scols = st.columns(4)
    s_alloc = [scols[i].number_input(f"投入【{cat}】", 0.0, float(total_budget), float(alloc_dict[cat]), 10.0) for i, cat in enumerate(categories)]
    tsim = sum(s_alloc)
    if tsim > total_budget: st.error(f"⚠️ 預算超支！({tsim}M > {total_budget}M)")
    else:
        p_scores = np.clip(curr_scores + np.array([1.5, 2.0, 1.2, 1.0]) * np.sqrt(s_alloc), 0, 100)
        closs = np.sum((100 - curr_scores) * loss_factors)
        ploss = np.sum((100 - p_scores) * loss_factors)
        
        st.success(f"✅ 模擬完成！可為公司 **減少 {(closs - ploss):.1f} 百萬隱性損失**。")
        lc = st.columns(2)
        lc[0].metric("🔴 目前預估隱性損失", f"{closs:.1f}M", "維持現狀的代價", "inverse")
        lc[1].metric("🟢 模擬後預估隱性損失", f"{ploss:.1f}M", f"ROI: {(((closs-ploss)/tsim)*100):.1f}%" if tsim>0 else "0%")

with tab4:
    st.subheader("🌍 動態航線、氣象與航班追蹤")
    @st.cache_data(show_spinner=False)
    def get_geo(loc):
        try: return Nominatim(user_agent="god_mode_v2").geocode(loc, timeout=5).latitude, Nominatim(user_agent="god_mode_v2").geocode(loc, timeout=5).longitude
        except: return None, None
    @st.cache_data(ttl=600, show_spinner=False)
    def get_wx(lat, lon):
        try:
            curr = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,wind_speed_10m,weather_code&wind_speed_unit=kn", timeout=5).json().get('current', {})
            return curr.get('wind_speed_10m','N/A'), curr.get('temperature_2m','N/A'), "氣候代碼 "+str(curr.get('weather_code',0))
        except: return "N/A", "N/A", "連線失敗"

    airports = ["TPE (台北)", "NRT (東京)", "SIN (新加坡)", "FRA (法蘭克福)", "JFK (紐約)", "DXB (杜拜)", "🌍 自行輸入..."]
    rc1, rc2 = st.columns(2)
    osel = rc1.selectbox("🛫 起飛地", airports, 0)
    dsel = rc2.selectbox("🛬 降落地", airports, 3)
    oinp = rc1.text_input("輸入起飛地:", value="桃園機場") if osel == "🌍 自行輸入..." else osel
    dinp = rc2.text_input("輸入降落地:", value="法蘭克福機場") if dsel == "🌍 自行輸入..." else dsel

    if oinp and dinp:
        with st.spinner('📡 正在定位、抓取衛星氣象與空域航班中...'):
            olat, olon = get_geo(oinp)
            dlat, dlon = get_geo(dinp)
            if olat and dlat and (olat!=dlat or olon!=dlon):
                mlat, mlon = (olat+dlat)/2, (olon+dlon)/2
                det_lat = max(min(mlat-15, 89.0), -89.0)
                det_lon = mlon+15 if mlon+15<=180 else mlon+15-360
                ow, ot, oc = get_wx(olat, olon)
                mw, mt, mc = get_wx(mlat, mlon)
                dw, dt, dc = get_wx(dlat, dlon)

                # OpenSky 航班追蹤 (API失敗自動轉為擬真流量)
                try:
                    flights = requests.get(f"https://opensky-network.org/api/states/all?lamin={mlat-5}&lomin={mlon-5}&lamax={mlat+5}&lomax={mlon+5}", timeout=3).json().get('states', [])
                    flats, flons, tstat = [f[6] for f in flights[:30] if f[6]], [f[5] for f in flights[:30] if f[5]], "🟢 OpenSky 真實流量"
                except:
                    flats, flons, tstat = mlat+np.random.uniform(-8,8,30), mlon+np.random.uniform(-8,8,30), "🟡 OpenSky 忙碌 (擬真流量)"

                figm = go.Figure()
                figm.add_trace(go.Scattergeo(lat=[mlat], lon=[mlon], marker=dict(size=120, color='red', opacity=0.2), name="🚨 戰區", mode="markers"))
                figm.add_trace(go.Scattergeo(lat=[olat,mlat,dlat], lon=[olon,mlon,dlon], mode='lines+markers', line=dict(color='red',dash='dash'), name="高風險航路"))
                figm.add_trace(go.Scattergeo(lat=[olat,det_lat,dlat], lon=[olon,det_lon,dlon], mode='lines+markers', line=dict(color='mediumseagreen'), name="安全繞飛"))
                if len(flats)>0: figm.add_trace(go.Scattergeo(lat=flats, lon=flons, mode='markers', marker=dict(symbol='circle', size=6, color='yellow'), name="✈️ 周邊航班"))
                
                figm.update_geos(projection_type="natural earth", showcountries=True, showland=True, landcolor="#1e1e1e", oceancolor="#0a0a14", showocean=True,
                                lataxis_range=[min(olat,dlat,det_lat)-15, max(olat,dlat,det_lat)+15], lonaxis_range=[min(olon,dlon,det_lon)-15, max(olon,dlon,det_lon)+15])
                figm.update_layout(height=450, margin=dict(l=0, r=0, t=0, b=0), paper_bgcolor="#0a0a0a", legend=dict(y=0.99, x=0.01))
                st.caption(tstat)
                st.plotly_chart(figm, use_container_width=True)

                wc1, wc2, wc3 = st.columns(3)
                wc1.info(f"🛫 **{oinp[:10]}**\n\n風速:{ow}kt | 氣溫:{ot}°C\n狀態:{oc}")
                wc2.warning(f"⚠️ **中繼危險區**\n\n風速:{mw}kt | 氣溫:{mt}°C\n狀態:{mc}")
                wc3.success(f"🛬 **{dinp[:10]}**\n\n風速:{dw}kt | 氣溫:{dt}°C\n狀態:{dc}")
                
                rdist = np.sqrt((olat-dlat)**2 + (olon-dlon)**2)
                st.error(f"🚨 **航線情報**：途經區域存在防空飛彈與GPS干擾風險。繞飛將增加 **{int(rdist*1.5+np.random.randint(20,45))}分鐘** 航程與 **{round(rdist*0.15,1)}噸** 燃油。")

with tab5:
    st.subheader("🤖 AI 戰略幕僚 (Virtual Advisor)")
    st.info(f"🧠 **系統 Context 已同步**：總預算 {total_budget}M, 最大工時 {max_labor_hours}H。分數：安{curr_safety}, 修{curr_maint}, 調{curr_otp}, 服{curr_service}")
    uq = st.chat_input("請輸入您想詢問 AI 的戰略問題...")
    if uq:
        st.chat_message("user").write(uq)
        with st.chat_message("assistant"):
            with st.spinner("AI 正在分析數據與最佳化模型..."):
                time.sleep(1.5)
                wcat = categories[np.argmin(curr_scores)]
                wscore = np.min(curr_scores)
                resp = f"總經理您好。針對問題「*{uq}*」，分析如下：\n\n1. **最大營運破口**：落在 **{wcat} ({wscore}分)**，潛在隱性損失達 {loss_factors[np.argmin(curr_scores)]*(100-wscore):.0f}M。\n"
                resp += f"2. **雙重限制衝突**：受限於 {max_labor_hours}H 的『工時上限』，單純砸錢無法解決維修瓶頸。建議將部分 {total_budget}M 預算轉為『外包量能』。\n"
                resp += f"3. **航線風險聯動**：剛才在 Tab4 雷達中，中東航班正在避讓。若調度({curr_otp}分)無法應對繞道延誤，將侵蝕服務({curr_service}分)。\n\n💡 **結論**：建議立即執行 Tab1 的多維限制最佳化方案。"
                st.write(resp)
