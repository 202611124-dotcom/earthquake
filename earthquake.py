import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# =========================
# 페이지 설정
# =========================
st.set_page_config(
    page_title="Earthquake Risk Dash",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 커스텀 스타일 (CSS)
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #1e2130; padding: 15px; border-radius: 10px; border: 1px solid #3e4250; }
    div.stButton > button:first-child {
        background-color: #ff4b4b; color: white; width: 100%; border-radius: 10px; height: 3em; font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# 데이터 불러오기 (캐싱 처리)
@st.cache_data
def load_data():
    return pd.read_csv("earthquake.csv")

df_new = load_data()

# 위험도 및 설정
risk_dict = {0: '🚨 매우 높음', 1: '✅ 낮음', 2: '⚠️ 중간'}
colors = {0: '#ff4b4b', 1: '#00d4ff', 2: '#faff00'} # 쌈뽕한 네온 컬러

# =========================
# 사이드바 (컨트롤 패널)
# =========================
with st.sidebar:
    st.title("🌍 분석 컨트롤")
    st.write("분석할 위치의 좌표를 입력하세요.")
    
    lat = st.number_input("📍 위도 (Latitude)", value=37.5, format="%.4f")
    lon = st.number_input("📍 경도 (Longitude)", value=127.0, format="%.4f")
    
    search_range = st.slider("🔍 분석 범위 (반경 도 단위)", 1, 10, 5)
    
    analyze_btn = st.button("분석 시작")
    
    st.divider()
    st.info("💡 Tip: 빨간색 점은 위험도가 높은 군집입니다.")

# =========================
# 메인 컨텐츠
# =========================
st.title("📊 세계 지진 위험도 분석 시스템")
st.caption("AI 기반 군집 분석 데이터를 활용하여 특정 지역의 지진 위험도를 실시간으로 평가합니다.")

if analyze_btn:
    with st.spinner('주변 데이터를 분석하는 중...'):
        # 주변 지진 데이터 필터링
        near_df = df_new[
            (df_new['위도'] >= lat - search_range) & (df_new['위도'] <= lat + search_range) &
            (df_new['경도'] >= lon - search_range) & (df_new['경도'] <= lon + search_range)
        ]

        if len(near_df) == 0:
            st.warning("⚠️ 해당 지역 반경 내에 축적된 지진 데이터가 부족하여 분석이 불가능합니다.")
        else:
            # 상단 메트릭 배치
            cluster_ratio = near_df['cluster'].value_counts(normalize=True)
            main_cluster = cluster_ratio.idxmax()
            
            m_col1, m_col2, m_col3 = st.columns(3)
            with m_col1:
                st.metric("예상 위험 등급", risk_dict[main_cluster])
            with m_col2:
                st.metric("주변 감지 데이터", f"{len(near_df)}건")
            with m_col3:
                st.metric("위험군 비중", f"{cluster_ratio.get(0, 0)*100:.1f}%")

            st.divider()

            # 지도 시각화
            st.subheader("🗺️ 지진 군집 분포 맵")
            
            # 다크 모드 타일 적용 (CartoDB dark_matter)
            m = folium.Map(location=[lat, lon], zoom_start=4, tiles="CartoDB dark_matter")

            # 데이터 샘플링 (성능 최적화)
            df_sample = df_new.sample(min(700, len(df_new)), random_state=42)

            for _, row in df_sample.iterrows():
                folium.CircleMarker(
                    location=[row['위도'], row['경도']],
                    radius=row['규모'] * 1.2, # 규모 강조
                    color=colors[row['cluster']],
                    fill=True,
                    fill_color=colors[row['cluster']],
                    fill_opacity=0.5,
                    weight=1
                ).add_to(m)

            # 사용자 위치 (별 모양 아이콘)
            folium.Marker(
                location=[lat, lon],
                popup="분석 지점",
                icon=folium.Icon(color='white', icon='star', icon_color='black')
            ).add_to(m)

            # 지도 출력
            st_folium(m, width="100%", height=600, returned_objects=[])
            
            st.success(f"📍 위도 {lat}, 경도 {lon} 주변 {search_range}도 범위 내 분석이 완료되었습니다.")

else:
    # 초기 화면 안내
    st.markdown("""
    <div style="text-align: center; padding: 100px; border: 2px dashed #3e4250; border-radius: 20px;">
        <h3>왼쪽 패널에서 좌표를 입력하고 '분석 시작' 버튼을 클릭하세요.</h3>
        <p>전 세계 지진 데이터를 시각화하고 잠재적 위험도를 평가합니다.</p>
    </div>
    """, unsafe_allow_html=True)
