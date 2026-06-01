import streamlit as st
import requests
import gspread
from google.oauth2.service_account import Credentials
import datetime

st.set_page_config(page_title="글로벌 축구 AI V5", page_icon="⚽", layout="wide")
st.title("⚽ 글로벌 AI 축구 예측기 V5 (최근 폼 & 배팅 가치 분석)")
st.write("AI가 최근 5경기 기세(Form)를 반영하여 승률을 예측하고, 실제 배당률 대비 베팅 가치(기댓값)를 찾아냅니다.")

# --- 1. API 및 구글 시트 세팅 ---
API_TOKEN = st.secrets["FOOTBALL_API_TOKEN"]
headers = {'X-Auth-Token': API_TOKEN}

try:
    scopes = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    credentials = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scopes)
    gc = gspread.authorize(credentials)
    SHEET_NAME = "축구_AI_분석기록" # 감독님 시트 이름
except Exception as e:
    st.warning("구글 시트 연동 대기 중 (분석 기능은 정상 작동합니다)")

# --- 2. 리그 및 팀 선택 파트 ---
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
    if res.status_code == 200:
        return res.json().get('matches', [])
    return []

matches = fetch_data(league_code)

# 최근 5경기 승점 계산 함수
def get_recent_form(team_name, all_matches):
    team_matches = [m for m in all_matches if team_name in m['homeTeam']['name'] or team_name in m['awayTeam']['name']]
    team_matches.sort(key=lambda x: x['utcDate'], reverse=True) # 최신순 정렬
    recent_5 = team_matches[:5]
    
    pts = 0
    for m in recent_5:
        is_home = team_name in m['homeTeam']['name']
        winner = m['score']['winner']
        if winner == 'DRAW': pts += 1
        elif (is_home and winner == 'HOME_TEAM') or (not is_home and winner == 'AWAY_TEAM'): pts += 3
    return pts # 최대 15점 만점

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

    # --- 3. 실전 프로토 배당률 입력 (V5 핵심 기능) ---
    st.write("---")
    st.subheader("💰 실전 프로토/배트맨 배당률 입력 (가치 검증)")
    st.info("실제 배당률을 입력하면 AI가 베팅할 가치가 있는지(수익 모델) 판단해 줍니다.")
    
    odds_h, odds_d, odds_a = st.columns(3)
    o_home = odds_h.number_input(f"🏠 {home_team} 승리 배당", value=2.00, step=0.1)
    o_draw = odds_d.number_input("🤝 무승부 배당", value=3.00, step=0.1)
    o_away = odds_a.number_input(f"✈️ {away_team} 승리 배당", value=2.50, step=0.1)

    if st.button("📊 AI 정밀 분석 및 배팅 가치 계산"):
        if home_team == away_team:
            st.warning("홈 팀과 원정 팀을 다르게 선택하세요!")
        else:
            with st.spinner('최근 5경기 폼과 득실차를 스캔 중입니다...'):
                h_matches, h_wins, h_scored, h_conceded, h_draws = 0, 0, 0, 0, 0
                a_matches, a_wins, a_scored, a_conceded, a_draws = 0, 0, 0, 0, 0
                
                for m in matches:
                    h_name, a_name = m['homeTeam']['name'], m['awayTeam']['name']
                    winner = m['score']['winner']
                    h_score = m['score']['fullTime'].get('home', 0) or 0
                    a_score = m['score']['fullTime'].get('away', 0) or 0
                    
                    if home_team in h_name:
                        h_matches += 1; h_scored += h_score; h_conceded += a_score
                        if winner == 'HOME_TEAM': h_wins += 1
                        elif winner == 'DRAW': h_draws += 1
                    if away_team in a_name:
                        a_matches += 1; a_scored += a_score; a_conceded += h_score
                        if winner == 'AWAY_TEAM': a_wins += 1
                        elif winner == 'DRAW': a_draws += 1
                
                if h_matches > 0 and a_matches > 0:
                    # 기본 스탯
                    h_win_rate = h_wins / h_matches * 100
                    a_win_rate = a_wins / a_matches * 100
                    draw_rate = ((h_draws/h_matches) + (a_draws/a_matches)) / 2 * 100
                    
                    # V5: 최근 5경기 폼(Form) 가져오기
                    h_form = get_recent_form(home_team, matches)
                    a_form = get_recent_form(away_team, matches)
                    
                    # 확률 가중치 계산 (기본 승률 + 득실차 + 폼)
                    h_pow = max(h_win_rate + (h_scored/h_matches*10) - (h_conceded/h_matches*10) + (h_form*2), 1)
                    a_pow = max(a_win_rate + (a_scored/a_matches*10) - (a_conceded/a_matches*10) + (a_form*2), 1)
                    d_pow = max(draw_rate + (15 - abs(h_pow - a_pow)*0.5), 1) # 전력이 비슷할수록 무승부 확률 증가
                    
                    total_pow = h_pow + a_pow + d_pow
                    prob_h = round((h_pow / total_pow) * 100, 1)
                    prob_d = round((d_pow / total_pow) * 100, 1)
                    prob_a = round((a_pow / total_pow) * 100, 1)
                    
                    st.success("✅ 전력 스캔 및 AI 기댓값 분석 완료!")
                    
                    # 최근 폼 출력
                    st.subheader("🔥 최근 5경기 기세 (Form)")
                    col_f1, col_f2 = st.columns(2)
                    col_f1.metric(f"🏠 {home_team}", f"{h_form}점 (15점 만점)", f"득실 {h_scored - h_conceded}")
                    col_f2.metric(f"✈️ {away_team}", f"{a_form}점 (15점 만점)", f"득실 {a_scored - a_conceded}")
                    
                    # 최종 확률 
                    st.write("---")
                    st.subheader("🤖 3-Way AI 승부 예측 확률")
                    c_h, c_d, c_a = st.columns(3)
                    c_h.write(f"**🏠 승리:** {prob_h}%")
                    c_d.write(f"**🤝 무승부:** {prob_d}%")
                    c_a.write(f"**✈️ 승리:** {prob_a}%")

                    # V5: 베팅 가치(Expected Value) 판독기
                    st.write("---")
                    st.subheader("💡 실전 배당률 가치(EV) 판독")
                    ev_h = round((prob_h / 100) * o_home, 2)
                    ev_d = round((prob_d / 100) * o_draw, 2)
                    ev_a = round((prob_a / 100) * o_away, 2)
                    
                    def show_ev(title, ev_val, odds):
                        if odds <= 0: return "배당률을 입력하세요"
                        if ev_val > 1.05: return f"🟢 **{title} (EV {ev_val}) - 꿀배당! 투자가치 높음**"
                        elif ev_val > 0.95: return f"🟡 **{title} (EV {ev_val}) - 적정 배당**"
                        else: return f"🔴 **{title} (EV {ev_val}) - 손해보는 배당 (패스 권장)**"

                    st.write(show_ev(f"{home_team} 승", ev_h, o_home))
                    st.write(show_ev("무승부", ev_d, o_draw))
                    st.write(show_ev(f"{away_team} 승", ev_a, o_away))
                    st.caption("* EV(기댓값)가 1.05 이상이면 스포츠 북(토토)보다 유리한 확률이라는 뜻입니다.")

                    # 구글 시트 기록
                    try:
                        now = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
                        record = [now.strftime('%Y-%m-%d %H:%M:%S'), selected_league, home_team, away_team, f"{prob_h}%", f"{prob_a}%", f"H:{ev_h}/A:{ev_a}"]
                        gc.open(SHEET_NAME).sheet1.append_row(record)
                        st.info("💾 분석 결과와 기댓값이 구글 시트에 저장되었습니다!")
                    except Exception:
                        pass
                else:
                    st.error("데이터가 부족합니다.")
