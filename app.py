import streamlit as st
import pandas as pd
import requests
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# 1. 페이지 설정
st.set_page_config(page_title="축구 AI 분석 시스템", page_icon="⚽", layout="wide")
st.title("⚽ 축구 AI 분석 시스템 V7 (세부 데이터 통합형)")

# 2. 인증 설정 (Secrets 사용)
API_TOKEN = st.secrets["FOOTBALL_API_TOKEN"]
headers = {'X-Auth-Token': API_TOKEN}

@st.cache_data(ttl=3600)
def get_fbref_stats():
    # FBref 프리미어리그 팀별 세부 통계 URL
    url = "https://fbref.com/en/comps/9/stats/Premier-League-Stats"
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers)
    tables = pd.read_html(res.text)
    return tables[0]

# 3. 사이드바 및 팀 선택
st.sidebar.header("설정")
if st.sidebar.button("📡 세부 데이터 갱신 (FBref)"):
    st.session_state.df = get_fbref_stats()

# 4. 분석 화면
if 'df' in st.session_state:
    df = st.session_state.df
    # 팀 이름 리스트 추출
    team_list = df['Squad'].tolist()
    
    col1, col2 = st.columns(2)
    home_team = col1.selectbox("🏠 홈 팀", team_list)
    away_team = col2.selectbox("✈️ 원정 팀", team_list)
    
    # 데이터 시각화
    st.subheader("📊 팀별 세부 전력 비교")
    comp_df = df[df['Squad'].isin([home_team, away_team])]
    st.dataframe(comp_df[['Squad', 'Gls', 'Ast', 'Cmp%', 'Sh', 'SoT']])

    # 5. 배팅 가치 분석 및 구글 시트 기록
    st.write("---")
    st.subheader("💰 실전 배당률 및 가치 분석")
    o_h = st.number_input("홈 승 배당", value=2.0)
    o_a = st.number_input("원정 승 배당", value=3.0)
    
    if st.button("📊 분석 결과 기록하기"):
        # 간단한 승률 계산 (득점력과 패스 성공률 기반 AI 공식)
        h_stats = df[df['Squad'] == home_team].iloc[0]
        a_stats = df[df['Squad'] == away_team].iloc[0]
        
        # 승률 계산 수식 (간소화)
        home_score = (h_stats['Gls'] * 1.5) + (h_stats['Cmp%'] * 0.2)
        away_score = (a_stats['Gls'] * 1.5) + (a_stats['Cmp%'] * 0.2)
        total = home_score + away_score
        
        p_h = round((home_score / total) * 100, 1)
        p_a = round((away_score / total) * 100, 1)
        
        st.write(f"🏠 홈팀 승리 확률: {p_h}% / ✈️ 원정팀 승리 확률: {p_a}%")
        
        # 구글 시트 저장
        try:
            scopes = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
            creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scopes)
            gc = gspread.authorize(creds)
            worksheet = gc.open("축구_AI_분석기록").sheet1
            worksheet.append_row([str(datetime.now()), home_team, away_team, f"{p_h}%", f"{p_a}%"])
            st.success("💾 분석 데이터가 구글 시트에 기록되었습니다!")
        except Exception as e:
            st.error(f"저장 실패: {e}")
else:
    st.info("왼쪽 사이드바에서 '데이터 갱신' 버튼을 눌러주세요.")
