import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="축구 AI 분석기 V8", page_icon="⚽", layout="wide")
st.title("⚽ 축구 AI 분석기 V8 (API 연동 버전)")

# API Key 설정 (스트림릿 Secrets에 저장한 키를 가져옵니다)
API_KEY = st.secrets["API_KEY"]
HEADERS = {
    "x-rapidapi-key": API_KEY,
    "x-rapidapi-host": "v3.football.api-sports.io"
}

# 데이터를 불러오는 핵심 함수
@st.cache_data(ttl=3600)
def get_api_data(endpoint):
    url = f"https://v3.football.api-sports.io/{endpoint}"
    response = requests.get(url, headers=HEADERS)
    return response.json()

# 리그 및 시즌 선택
st.sidebar.header("데이터 선택")
league_id = 39 # EPL 리그 ID (API-Football 기준)
season = 2025

if st.sidebar.button("📡 API로 최신 순위 가져오기"):
    with st.spinner("전문 데이터를 불러오는 중..."):
        try:
            data = get_api_data(f"standings?league={league_id}&season={season}")
            standings = data['response'][0]['league']['standings'][0]
            
            # 데이터를 보기 좋게 정리
            df_list = []
            for team in standings:
                df_list.append({
                    "순위": team['rank'],
                    "팀": team['team']['name'],
                    "승점": team['points'],
                    "득점": team['all']['goals']['for'],
                    "실점": team['all']['goals']['against'],
                    "승": team['all']['win'],
                    "무": team['all']['draw'],
                    "패": team['all']['lose']
                })
            st.session_state.df = pd.DataFrame(df_list)
            st.success("✅ 데이터 로드 성공!")
        except Exception as e:
            st.error(f"데이터 로드 실패: {e}")

# 화면 표시
if 'df' in st.session_state:
    st.dataframe(st.session_state.df, use_container_width=True)
    st.write("💡 이 데이터는 API-Football로부터 실시간으로 제공받은 신뢰할 수 있는 데이터입니다.")
