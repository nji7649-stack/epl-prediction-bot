import streamlit as st
import requests
import gspread
from google.oauth2.service_account import Credentials
import datetime

st.set_page_config(page_title="글로벌 축구 AI V4", page_icon="🌍", layout="wide")
st.title("🌍 글로벌 AI 축구 예측기 + 📝 구글 시트 자동 기록")

# --- 설정 및 인증 파트 ---
API_TOKEN = st.secrets["FOOTBALL_API_TOKEN"]
headers = {'X-Auth-Token': API_TOKEN}

# 구글 시트 연결 세팅
scopes = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]
# 스트림릿 금고에서 구글 접속 열쇠를 꺼내옵니다.
credentials = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"], scopes=scopes
)
gc = gspread.authorize(credentials)

# 💡 감독님이 만드신 구글 시트의 정확한 파일 이름을 아래에 적어주세요!
SHEET_NAME = "축구_AI_분석기록" 

# --- 앱 로직 파트 ---
leagues = {
    "🇬🇧 영국 프리미어리그 (EPL)": "PL",
    "🇪🇸 스페인 라리가": "PD",
    "🇮🇹 이탈리아 세리에 A": "SA",
    "🇩🇪 독일 분데스리가": "BL1",
    "🇫🇷 프랑스 리그 1": "FL1"
}

selected_league = st.selectbox("🏆 분석할 리그 선택", list(leagues.keys()))
league_code = leagues[selected_league]

@st.cache_data(ttl=3600)
def fetch_data(comp_code):
    url = f'https://api.football-data.org/v4/competitions/{comp_code}/matches?status=FINISHED'
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        return res.json().get('matches', [])
    return []

matches = fetch_data(league_code)

if matches:
    team_set = set()
    for m in matches:
        team_set.add(m['homeTeam']['name'])
        team_set.add(m['awayTeam']['name'])
    team_list = sorted(list(team_set))
    
    st.write("---")
    col1, col2 = st.columns(2)
    with col1: home_team = st.selectbox("🏠 홈 팀", team_list, index=0)
    with col2: away_team = st.selectbox("✈️ 원정 팀", team_list, index=1 if len(team_list) > 1 else 0)

    if st.button("📊 분석 및 결과 기록하기"):
        if home_team == away_team:
            st.warning("홈 팀과 원정 팀을 다르게 선택하세요!")
        else:
            with st.spinner('분석 중...'):
                home_matches, home_wins, home_scored, home_conceded = 0, 0, 0, 0
                away_matches, away_wins, away_scored, away_conceded = 0, 0, 0, 0
                
                for m in matches:
                    h_name, a_name = m['homeTeam']['name'], m['awayTeam']['name']
                    winner = m['score']['winner']
                    h_score = m['score']['fullTime'].get('home', 0) or 0
                    a_score = m['score']['fullTime'].get('away', 0) or 0
                    
                    if home_team in h_name:
                        home_matches += 1
                        home_scored += h_score
                        home_conceded += a_score
                        if winner == 'HOME_TEAM': home_wins += 1
                    if away_team in a_name:
                        away_matches += 1
                        away_scored += a_score
                        away_conceded += h_score
                        if winner == 'AWAY_TEAM': away_wins += 1
                
                if home_matches > 0 and away_matches > 0:
                    home_win_rate = (home_wins / home_matches) * 100
                    away_win_rate = (away_wins / away_matches) * 100
                    
                    avg_h_scored = home_scored / home_matches
                    avg_h_conceded = home_conceded / home_matches
                    avg_a_scored = away_scored / away_matches
                    avg_a_conceded = away_conceded / away_matches
                    
                    # 승률 예측 계산
                    h_pow = max(home_win_rate + (avg_h_scored * 15) - (avg_h_conceded * 15), 1)
                    a_pow = max(away_win_rate + (avg_a_scored * 15) - (avg_a_conceded * 15), 1)
                    t_pow = h_pow + a_pow
                    home_prob = round((h_pow / t_pow) * 100, 1)
                    away_prob = round((a_pow / t_pow) * 100, 1)
                    
                    # 1. 화면에 결과 출력
                    st.success("✅ 전력 스캔 및 AI 분석 완료!")
                    st.subheader("🤖 득실차 반영 승부 예측")
                    st.write(f"🏠 **{home_team}** 승리 확률: **{home_prob}%**")
                    st.progress(int(home_prob))
                    st.write(f"✈️ **{away_team}** 승리 확률: **{away_prob}%**")
                    st.progress(int(away_prob))

                    # 📝 2. 구글 시트에 자동 기록!
                    try:
                        # 한국 시간(KST)으로 기록
                        now = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
                        time_str = now.strftime('%Y-%m-%d %H:%M:%S')
                        
                        # 시트 열고 데이터 쓰기
                        worksheet = gc.open(SHEET_NAME).sheet1
                        record = [time_str, selected_league, home_team, away_team, f"{home_prob}%", f"{away_prob}%"]
                        worksheet.append_row(record)
                        st.info("💾 (시스템 알림) 분석 결과가 구글 시트에 안전하게 자동 저장되었습니다!")
                    except Exception as e:
                        st.error(f"⚠️ 구글 시트 저장 실패: {e}")
                else:
                    st.error("데이터 부족!")
