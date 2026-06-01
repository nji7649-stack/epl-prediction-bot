import streamlit as st
import requests
import gspread
from google.oauth2.service_account import Credentials
import datetime

# 1. 웹사이트 설정
st.set_page_config(page_title="글로벌 축구 AI V6", page_icon="⚽", layout="wide")
st.title("⚽ 글로벌 AI 축구 예측기 V6 (종합 분석 시스템)")
st.write("최근 기세(폼), 공격/수비력, 그리고 배당률 기댓값까지 분석하여 시트에 기록합니다.")

# 2. API 및 보안 설정 (스트림릿 Secrets 금고 사용)
API_TOKEN = st.secrets["FOOTBALL_API_TOKEN"]
headers = {'X-Auth-Token': API_TOKEN}

# 구글 시트 연결
try:
    scopes = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    credentials = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scopes)
    gc = gspread.authorize(credentials)
    SHEET_NAME = "축구_AI_분석기록" 
except:
    st.error("구글 시트 인증 정보를 확인해주세요.")

# 3. 최근 5경기 기세(Form) 계산 함수
def get_recent_form(team_name, all_matches):
    team_matches = [m for m in all_matches if team_name in m['homeTeam']['name'] or team_name in m['awayTeam']['name']]
    team_matches.sort(key=lambda x: x['utcDate'], reverse=True)
    recent_5 = team_matches[:5]
    pts = 0
    for i, m in enumerate(recent_5):
        weight = 5 - i 
        is_home = team_name in m['homeTeam']['name']
        winner = m['score']['winner']
        if winner == 'DRAW': pts += (1 * weight)
        elif (is_home and winner == 'HOME_TEAM') or (not is_home and winner == 'AWAY_TEAM'): pts += (3 * weight)
    return pts

# 4. 리그 및 팀 선택
leagues = {
    "🇬🇧 영국 프리미어리그 (EPL)": "PL", "🇪🇸 스페인 라리가": "PD",
    "🇮🇹 이탈리아 세리에 A": "SA", "🇩🇪 독일 분데스리가": "BL1", "🇫🇷 프랑스 리그 1": "FL1"
}
selected_league = st.selectbox("🏆 분석할 리그 선택", list(leagues.keys()))
league_code = leagues[selected_league]

@st.cache_data(ttl=3600)
def fetch_data(comp_code):
    url = f'https://api.football-data.org/v4/competitions/{comp_code}/matches?status=FINISHED'
    res = requests.get(url, headers=headers)
    return res.json().get('matches', []) if res.status_code == 200 else []

matches = fetch_data(league_code)

if matches:
    team_set = {m['homeTeam']['name'] for m in matches} | {m['awayTeam']['name'] for m in matches}
    team_list = sorted(list(team_set))
    
    col1, col2 = st.columns(2)
    home_team = col1.selectbox("🏠 홈 팀", team_list, index=0)
    away_team = col2.selectbox("✈️ 원정 팀", team_list, index=1 if len(team_list) > 1 else 0)
    
    # 배당률 입력
    st.write("---")
    st.subheader("💰 실전 프로토 배당률")
    o_home, o_draw, o_away = st.columns(3)
    odds_h = o_home.number_input("🏠 홈 승 배당", value=2.00, step=0.1)
    odds_d = o_draw.number_input("🤝 무승부 배당", value=3.20, step=0.1)
    odds_a = o_away.number_input("✈️ 원정 승 배당", value=2.50, step=0.1)

    if st.button("📊 AI 정밀 분석 및 기록"):
        h_m, h_w, h_sc, h_cn = 0, 0, 0, 0
        a_m, a_w, a_sc, a_cn = 0, 0, 0, 0
        
        for m in matches:
            if home_team in m['homeTeam']['name']:
                h_m += 1; h_sc += (m['score']['fullTime'].get('home') or 0); h_cn += (m['score']['fullTime'].get('away') or 0)
                if m['score']['winner'] == 'HOME_TEAM': h_w += 1
            if away_team in m['awayTeam']['name']:
                a_m += 1; a_sc += (m['score']['fullTime'].get('away') or 0); a_cn += (m['score']['fullTime'].get('home') or 0)
                if m['score']['winner'] == 'AWAY_TEAM': a_w += 1
        
        if h_m > 0 and a_m > 0:
            h_form, a_form = get_recent_form(home_team, matches), get_recent_form(away_team, matches)
            # 확률 계산
            h_pow = max((h_w/h_m*100) + (h_sc/h_m*15) - (h_cn/h_m*15) + (h_form*2), 1)
            a_pow = max((a_w/a_m*100) + (a_sc/a_m*15) - (a_cn/a_m*15) + (a_form*2), 1)
            t_pow = h_pow + a_pow
            p_h = round((h_pow / t_pow) * 100, 1)
            p_a = round((a_pow / t_pow) * 100, 1)
            
            st.success("✅ AI 분석 완료!")
            st.metric(f"🏠 {home_team} vs ✈️ {away_team} 승리 확률", f"{p_h}% vs {p_a}%")
            
            # 배팅 가치 검증
            ev_h = round((p_h / 100) * odds_h, 2)
            ev_a = round((p_a / 100) * odds_a, 2)
            st.write(f"💡 홈팀 기댓값(EV): {ev_h} {'(꿀배당!)' if ev_h > 1.05 else '(패스)'}")
            st.write(f"💡 원정팀 기댓값(EV): {ev_a} {'(꿀배당!)' if ev_a > 1.05 else '(패스)'}")
            
            # 구글 시트 저장
            worksheet = gc.open(SHEET_NAME).sheet1
            worksheet.append_row([str(datetime.datetime.now()), selected_league, home_team, away_team, f"{p_h}%", f"{p_a}%"])
            st.info("💾 분석 결과가 시트에 저장되었습니다.")
