import streamlit as st
import requests

# 1. 웹사이트 기본 설정
st.set_page_config(page_title="글로벌 축구 AI V3", page_icon="🌍", layout="wide")
st.title("🌍 글로벌 AI 축구 예측기 (유럽 5대 리그)")
st.write("프리미어리그를 넘어 스페인, 이탈리아, 독일, 프랑스 리그까지 전 세계 최고 팀들의 승부를 예측합니다.")

# 2. API 설정 (비밀 금고에서 키 가져오기)
API_TOKEN = st.secrets["FOOTBALL_API_TOKEN"]
headers = {'X-Auth-Token': API_TOKEN}

# 3. 리그 선택 메뉴 생성 (무료로 제공되는 유럽 5대 리그)
leagues = {
    "🇬🇧 영국 프리미어리그 (EPL)": "PL",
    "🇪🇸 스페인 라리가": "PD",
    "🇮🇹 이탈리아 세리에 A": "SA",
    "🇩🇪 독일 분데스리가": "BL1",
    "🇫🇷 프랑스 리그 1": "FL1"
}

# 사용자 리그 선택창
selected_league = st.selectbox("🏆 분석할 리그를 먼저 선택하세요!", list(leagues.keys()))
league_code = leagues[selected_league]

# 4. 데이터 긁어오기 & 캐싱 (매번 통신하면 API가 차단될 수 있으므로 임시 저장 기능 추가)
@st.cache_data(ttl=3600)
def fetch_data(comp_code):
    url = f'https://api.football-data.org/v4/competitions/{comp_code}/matches?status=FINISHED'
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        return res.json().get('matches', [])
    return []

with st.spinner(f'{selected_league} 최신 경기 데이터를 불러오는 중...'):
    matches = fetch_data(league_code)

# 5. 팀 목록 자동 추출 및 분석 파트
if matches:
    # 매치 데이터에서 팀 이름만 자동으로 뽑아내어 리스트 만들기 (수작업 노가다 방지!)
    team_set = set()
    for m in matches:
        team_set.add(m['homeTeam']['name'])
        team_set.add(m['awayTeam']['name'])
    team_list = sorted(list(team_set))
    
    st.write("---")
    col1, col2 = st.columns(2)
    with col1:
        home_team = st.selectbox("🏠 홈 팀 선택", team_list, index=0)
    with col2:
        # 두 번째 팀을 기본 원정 팀으로 세팅
        away_team = st.selectbox("✈️ 원정 팀 선택", team_list, index=1 if len(team_list) > 1 else 0)

    if st.button("📊 글로벌 AI 분석 가동"):
        if home_team == away_team:
            st.warning("⚠️ 홈 팀과 원정 팀을 다르게 선택해주세요!")
        else:
            with st.spinner('해당 리그의 골 득실과 승률 데이터를 분석 중입니다...'):
                home_matches, home_wins, home_scored, home_conceded = 0, 0, 0, 0
                away_matches, away_wins, away_scored, away_conceded = 0, 0, 0, 0
                
                # 선택한 두 팀의 전적만 추려내기
                for m in matches:
                    h_name = m['homeTeam']['name']
                    a_name = m['awayTeam']['name']
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
                    
                    avg_home_scored = home_scored / home_matches
                    avg_home_conceded = home_conceded / home_matches
                    avg_away_scored = away_scored / away_matches
                    avg_away_conceded = away_conceded / away_matches
                    
                    st.success("✅ 글로벌 전력 스캔 및 AI 분석 완료!")
                    
                    st.subheader(f"🔥 {selected_league} 팀별 상세 전투력")
                    c1, c2, c3 = st.columns(3)
                    c1.metric(f"🏠 {home_team}", f"{round(home_win_rate, 1)}% 승률")
                    c2.metric("평균 득점 (공격력)", f"{round(avg_home_scored, 2)}골")
                    c3.metric("평균 실점 (수비력)", f"{round(avg_home_conceded, 2)}골")
                    
                    c4, c5, c6 = st.columns(3)
                    c4.metric(f"✈️ {away_team}", f"{round(away_win_rate, 1)}% 승률")
                    c5.metric("평균 득점 (공격력)", f"{round(avg_away_scored, 2)}골")
                    c6.metric("평균 실점 (수비력)", f"{round(avg_away_conceded, 2)}골")
                    
                    # 득실차 가중치 적용 예측 알고리즘
                    home_power = home_win_rate + (avg_home_scored * 15) - (avg_home_conceded * 15)
                    away_power = away_win_rate + (avg_away_scored * 15) - (avg_away_conceded * 15)
                    
                    home_power = max(home_power, 1)
                    away_power = max(away_power, 1)
                    
                    total_power = home_power + away_power
                    home_prob = (home_power / total_power) * 100
                    away_prob = (away_power / total_power) * 100
                    
                    st.write("---")
                    st.subheader("🤖 득실차 반영 최종 승부 예측")
                    st.write(f"🏠 **{home_team}** 승리 확률: **{round(home_prob, 1)}%**")
                    st.progress(int(home_prob))
                    
                    st.write(f"✈️ **{away_team}** 승리 확률: **{round(away_prob, 1)}%**")
                    st.progress(int(away_prob))
                else:
                    st.error("아직 충분한 경기 데이터가 없습니다.")
else:
    st.error("데이터를 가져오는 데 실패했습니다. API 키 문제이거나 서버 지연일 수 있습니다.")
