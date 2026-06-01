import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# =========================
# 페이지 설정 (가독성 중심)
# =========================
st.set_page_config(
    page_title="지진 위험도 분석",
    page_icon="🌍",
    layout="wide"
)

# 글씨가 잘 보이도록 강제 폰트 색상 지정 (CSS)
st.markdown("""
    <style>
    /* 전체 글자색을 진하게 */
    .main, .stMarkdown, p, h1, h2, h3 {
        color: #1A1A1A !important;
    }
    /* 지표(Metric) 박스 디자인 가독성 강화 */
    [data-testid="stMetricValue"] {
        color: #D32F2F !important; /* 강조색 */
        font-weight: bold;
    }
    /* 사이드바 가독성 */
    .css-1d391kg, .st-eb {
        background-color: #F8F9FA;
    }
    </style>
    """, unsafe_allow_html=True)

# 데이터 불러오기
@st.cache_data
def load_data():
    return pd.read_csv("earthquake.csv")

df_new = load_data()

# 위험도 및 고대비 색상 설정
risk_dict = {0: '🔴 위험도 높음', 1: '🔵 위험도 낮음', 2: '🟢 위험도 중간'}
# 지도에서 잘 보이는 명확한 원색 계열 사용
colors = {0: '#FF0000', 1: '#007BFF', 2: '#28A745'}

# =========================
# 사이드바 설정
# =========================
with st.sidebar:
    st.header("📍 위치 입력")
    st.write("분석할 위도와 경도를 입력하세요.")
    
    lat = st.number_input("위도 (Latitude)", value=37.5, format="%.4f")
    lon = st.number_input("경도 (Longitude)", value=127.0, format="%.4f")
    
    st.divider()
    analyze_btn = st.button("🔍 위험도 분석 시작", type="primary")

# =========================
# 메인 컨텐츠
# =========================
st.title("🌍 세계 지진 위험도 분석 시스템")
st.write("입력하신 좌표 주변의 과거 지진 데이터를 분석하여 현재 위치의 위험도를 평가합니다.")

if analyze_btn:
    # 1. 주변 데이터 필터링 (반경 5도)
    near_df = df_new[
        (df_new['위도'] >= lat - 5) & (df_new['위도'] <= lat + 5) &
        (df_new['경도'] >= lon - 5) & (df_new['경도'] <= lon + 5)
    ]

    if len(near_df) == 0:
        st.error("❌ 분석 불가: 해당 지역 근처에 지진 데이터가 존재하지 않습니다.")
    else:
        # 2. 결과 계산
        cluster_ratio = near_df['cluster'].value_counts(normalize=True)
        main_cluster = cluster_ratio.idxmax()

        # 3. 분석 결과 상단 배치 (Metric)
        st.subheader("📊 분석 결과 요약")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("종합 위험도", risk_dict[main_cluster])
        with c2:
            st.metric("검색된 지진 수", f"{len(near_df)}건")
        with c3:
            st.metric("최대 비중 군집", f"{cluster_ratio.max()*100:.1f}%")

        st.divider()

        # 4. 지도 시각화 (가장 밝은 'CartoDB positron' 사용)
        st.subheader("🗺️ 지진 데이터 분포도")
        m = folium.Map(location=[lat, lon], zoom_start=5, tiles="CartoDB positron")

        # 샘플링 데이터 표시 (원본 코드 로직 유지)
        df_sample = df_new.sample(min(500, len(df_new)), random_state=42)

        for _, row in df_sample.iterrows():
            folium.CircleMarker(
                location=[row['위도'], row['경도']],
                radius=row['규모'] * 1.5,
                color=colors[row['cluster']],
                fill=True,
                fill_color=colors[row['cluster']],
                fill_opacity=0.6
            ).add_to(m)

        # 사용자 입력 위치 (검정색 핀)
        folium.Marker(
            location=[lat, lon],
            popup="분석 위치",
            icon=folium.Icon(color='black', icon='info-sign')
        ).add_to(m)

        st_folium(m, width="100%", height=600, returned_objects=[])

else:
    st.info("왼쪽 사이드바에서 위치를 입력한 후 '분석 시작' 버튼을 눌러주세요.")
