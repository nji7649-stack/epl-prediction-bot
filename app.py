import streamlit as st
import requests

# 1. 웹사이트 제목과 꾸미기
st.title("⚽ 프리미어리그 AI 분석 대시보드")
st.write("원하는 팀의 데이터를 검색하고 승률을 시각화하여 확인하세요!")

# 2. 깃허브가 아닌 '스트림릿 금고'에서 API 키를 꺼내옵니다.
API_TOKEN = st.secrets["FOOTBALL_API_TOKEN"]
headers = {'X-Auth-Token': API_TOKEN}

# 3. 사용자에게 팀 이름을 직접 입력받는 텍스트 박스 만들기
target_team = st.text_input("🔍 분석할 팀 이름을 영어로 입력하세요 (예: Manchester City, Arsenal, Tottenham)", "Manchester City")

# 4. '분석 시작' 버튼 만들기
if st.button("데이터 분석 시작"):
    with st.spinner('데이터를 불러오고 분석하는 중입니다...'):
        url = 'https://api.football-data.org/v4/competitions/PL/matches?status=FINISHED'
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            matches = data.get('matches', [])
            
            team_matches, wins, draws, losses = 0, 0, 0, 0
            
            for match in matches:
                home = match['homeTeam']['name']
                away = match['awayTeam']['name']
                winner = match['score']['winner']
                
                if target_team in home:
                    team_matches += 1
                    if winner == 'HOME_TEAM': wins += 1
                    elif winner == 'DRAW': draws += 1
                    else: losses += 1
                elif target_team in away:
                    team_matches += 1
                    if winner == 'AWAY_TEAM': wins += 1
                    elif winner == 'DRAW': draws += 1
                    else: losses += 1
            
            if team_matches == 0:
                st.error("❌ 팀을 찾을 수 없습니다. 스펠링을 확인해주세요.")
            else:
                st.success(f"✅ [{target_team}] 데이터 분석 완료!")
                
                # 📊 시각화 1: 핵심 데이터 표시 (숫자 위젯)
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("총 경기수", f"{team_matches}경기")
                col2.metric("승리", f"{wins}승")
                col3.metric("무승부", f"{draws}무")
                col4.metric("패배", f"{losses}패")
                
                win_rate = round((wins/team_matches)*100, 1)
                st.metric("🏆 시즌 승률", f"{win_rate}%")
                
                # 📊 시각화 2: 막대 그래프
                st.write("### 📈 경기 결과 요약 차트")
                chart_data = {"결과": ["승리", "무승부", "패배"], "경기수": [wins, draws, losses]}
                st.bar_chart(chart_data, x="결과", y="경기수")
                
        else:
            st.error("데이터 통신에 실패했습니다.")
