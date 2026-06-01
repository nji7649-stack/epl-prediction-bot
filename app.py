import streamlit as st
import requests

# 1. 웹사이트 기본 설정
st.set_page_config(page_title="EPL AI 시뮬레이터", page_icon="⚽")
st.title("⚽ EPL AI 가상 매치업 시뮬레이터")
st.write("오타 걱정 없이 팀을 선택하세요! AI가 두 팀의 데이터를 비교해 승리 확률을 예측합니다.")

# 2. API 키 설정 (스트림릿 금고에서 가져옴)
API_TOKEN = st.secrets["FOOTBALL_API_TOKEN"]
headers = {'X-Auth-Token': API_TOKEN}

# 3. 프리미어리그 20개 팀 목록 (드롭다운용)
epl_teams = [
    "Arsenal", "Aston Villa", "Bournemouth", "Brentford", "Brighton",
    "Burnley", "Chelsea", "Crystal Palace", "Everton", "Fulham",
    "Liverpool", "Luton", "Manchester City", "Manchester United",
    "Newcastle", "Nottingham", "Sheffield", "Tottenham", "West Ham", "Wolverhampton"
]

# 4. 화면을 반으로 나누어 홈팀/원정팀 선택 상자(드롭다운) 만들기
col1, col2 = st.columns(2)
with col1:
    home_team = st.selectbox("🏠 홈 팀 선택", epl_teams, index=17) # 토트넘 기본값
with col2:
    away_team = st.selectbox("✈️ 원정 팀 선택", epl_teams, index=0) # 아스널 기본값

# 5. 분석 시작 버튼
if st.button("📊 데이터 분석 및 AI 예측 가동"):
    if home_team == away_team:
        st.warning("⚠️ 홈 팀과 원정 팀을 다르게 선택해주세요!")
    else:
        with st.spinner('과거 데이터를 불러와 AI가 분석 중입니다...'):
            url = 'https://api.football-data.org/v4/competitions/PL/matches?status=FINISHED'
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                matches = response.json().get('matches', [])
                
                # 데이터 수집 변수
                home_matches, home_wins = 0, 0
                away_matches, away_wins = 0, 0
                
                # 전적 계산 로직 (홈팀의 홈 성적 vs 원정팀의 원정 성적)
                for m in matches:
                    h_name = m['homeTeam']['name']
                    a_name = m['awayTeam']['name']
                    winner = m['score']['winner']
                    
                    if home_team in h_name:
                        home_matches += 1
                        if winner == 'HOME_TEAM': home_wins += 1
                        
                    if away_team in a_name:
                        away_matches += 1
                        if winner == 'AWAY_TEAM': away_wins += 1
                
                # 승률 계산
                if home_matches > 0 and away_matches > 0:
                    home_win_rate = (home_wins / home_matches) * 100
                    away_win_rate = (away_wins / away_matches) * 100
                    
                    st.success("✅ AI 분석 완료!")
                    
                    # 📈 1. 전력 비교 시각화
                    st.subheader("📈 양 팀 이번 시즌 강점 비교")
                    col3, col4 = st.columns(2)
                    col3.metric(f"🏠 {home_team} (홈 승률)", f"{round(home_win_rate, 1)}%")
                    col4.metric(f"✈️ {away_team} (원정 승률)", f"{round(away_win_rate, 1)}%")
                    
                    # 🤖 2. AI 승부 예측 알고리즘
                    st.subheader("🤖 AI 승부 예측 결과")
                    total_power = home_win_rate + away_win_rate
                    
                    if total_power == 0:
                        st.info("두 팀 모두 승률이 너무 낮아 무승부 확률이 높습니다.")
                    else:
                        # 홈/원정 승률을 기반으로 한 가중치 예측
                        home_prob = (home_win_rate / total_power) * 100
                        away_prob = (away_win_rate / total_power) * 100
                        
                        st.write(f"🔥 **{home_team}** 승리 확률: **{round(home_prob, 1)}%**")
                        st.progress(int(home_prob)) # 게이지 바로 표현
                        
                        st.write(f"❄️ **{away_team}** 승리 확률: **{round(away_prob, 1)}%**")
                        st.progress(int(away_prob))
                else:
                    st.error("데이터를 찾을 수 없습니다.")
            else:
                st.error("API 통신 에러 발생!")
