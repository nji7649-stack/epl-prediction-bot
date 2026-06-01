import streamlit as st
import requests

# 1. 웹사이트 기본 설정 (화면을 넓게 씁니다)
st.set_page_config(page_title="EPL AI 시뮬레이터 V2", page_icon="⚽", layout="wide")
st.title("⚽ EPL AI 예측기 (골 득실 & 전투력 탑재)")
st.write("단순 승률을 넘어, 팀의 평균 공격력(득점)과 수비력(실점)까지 종합적으로 계산하여 예측합니다.")

# 2. API 키 설정
API_TOKEN = st.secrets["FOOTBALL_API_TOKEN"]
headers = {'X-Auth-Token': API_TOKEN}

epl_teams = [
    "Arsenal", "Aston Villa", "Bournemouth", "Brentford", "Brighton",
    "Burnley", "Chelsea", "Crystal Palace", "Everton", "Fulham",
    "Liverpool", "Luton", "Manchester City", "Manchester United",
    "Newcastle", "Nottingham", "Sheffield", "Tottenham", "West Ham", "Wolverhampton"
]

col1, col2 = st.columns(2)
with col1:
    home_team = st.selectbox("🏠 홈 팀 선택", epl_teams, index=17)
with col2:
    away_team = st.selectbox("✈️ 원정 팀 선택", epl_teams, index=0)

if st.button("📊 AI 정밀 분석 가동"):
    if home_team == away_team:
        st.warning("⚠️ 홈 팀과 원정 팀을 다르게 선택해주세요!")
    else:
        with st.spinner('승률, 득점력, 수비력 데이터를 긁어와 AI가 계산 중입니다...'):
            url = 'https://api.football-data.org/v4/competitions/PL/matches?status=FINISHED'
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                matches = response.json().get('matches', [])
                
                # 변수 준비 (승패 및 골 득실)
                home_matches, home_wins, home_scored, home_conceded = 0, 0, 0, 0
                away_matches, away_wins, away_scored, away_conceded = 0, 0, 0, 0
                
                # 데이터 긁어오기 로직
                for m in matches:
                    h_name = m['homeTeam']['name']
                    a_name = m['awayTeam']['name']
                    winner = m['score']['winner']
                    
                    # 골 데이터 가져오기 (에러 방지를 위해 0으로 기본값 설정)
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
                
                # AI 통계 계산
                if home_matches > 0 and away_matches > 0:
                    # 1. 승률
                    home_win_rate = (home_wins / home_matches) * 100
                    away_win_rate = (away_wins / away_matches) * 100
                    
                    # 2. 평균 득점 (공격력) & 평균 실점 (수비력)
                    avg_home_scored = home_scored / home_matches
                    avg_home_conceded = home_conceded / home_matches
                    
                    avg_away_scored = away_scored / away_matches
                    avg_away_conceded = away_conceded / away_matches
                    
                    st.success("✅ 전력 스캔 및 AI 분석 완료!")
                    
                    # --- 화면 출력부 ---
                    st.subheader("🔥 팀별 상세 전투력 (홈 vs 원정 기준)")
                    
                    # 홈팀 스탯
                    c1, c2, c3 = st.columns(3)
                    c1.metric(f"🏠 {home_team} 승률", f"{round(home_win_rate, 1)}%")
                    c2.metric("평균 득점 (공격력)", f"{round(avg_home_scored, 2)}골")
                    c3.metric("평균 실점 (수비력)", f"{round(avg_home_conceded, 2)}골")
                    
                    # 원정팀 스탯
                    c4, c5, c6 = st.columns(3)
                    c4.metric(f"✈️ {away_team} 승률", f"{round(away_win_rate, 1)}%")
                    c5.metric("평균 득점 (공격력)", f"{round(avg_away_scored, 2)}골")
                    c6.metric("평균 실점 (수비력)", f"{round(avg_away_conceded, 2)}골")
                    
                    # --- AI 승부 예측 알고리즘 (가중치 부여) ---
                    # 전투력 = 기본 승률 + (평균 득점 * 15점 가산점) - (평균 실점 * 15점 감점)
                    home_power = home_win_rate + (avg_home_scored * 15) - (avg_home_conceded * 15)
                    away_power = away_win_rate + (avg_away_scored * 15) - (avg_away_conceded * 15)
                    
                    # 마이너스 점수 방지
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
                    st.error("데이터를 찾을 수 없습니다.")
            else:
                st.error("API 통신 에러 발생!")
