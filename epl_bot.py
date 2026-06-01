import requests
import os

# 1. 금고에서 API 키 꺼내기
API_TOKEN = os.environ.get('FOOTBALL_API_TOKEN')
headers = {'X-Auth-Token': API_TOKEN}

# 2. 프리미어리그(PL)의 '종료된 경기(FINISHED)' 전체 데이터를 요청합니다!
url = 'https://api.football-data.org/v4/competitions/PL/matches?status=FINISHED'

response = requests.get(url, headers=headers)

if response.status_code == 200:
    data = response.json()
    matches = data.get('matches', [])
    
    total_matches = len(matches)
    home_wins = 0
    away_wins = 0
    draws = 0
    
    # 3. 로봇이 모든 경기를 하나씩 확인하며 승무패를 셉니다.
    for match in matches:
        winner = match['score']['winner'] # 이긴 팀이 누군지 확인
        if winner == 'HOME_TEAM':
            home_wins += 1
        elif winner == 'AWAY_TEAM':
            away_wins += 1
        elif winner == 'DRAW':
            draws += 1
            
    # 4. 분석 결과 출력 (승률 계산: 승리 횟수 / 전체 경기 수 * 100)
    print("⚽ [프리미어리그 23/24 시즌 최종 승률 분석] ⚽\n")
    print(f"📊 총 분석 경기 수: {total_matches}경기")
    print(f"🏠 홈팀 승리: {home_wins}경기 (승률: {round(home_wins/total_matches*100, 1)}%)")
    print(f"✈️ 원정팀 승리: {away_wins}경기 (승률: {round(away_wins/total_matches*100, 1)}%)")
    print(f"🤝 무승부: {draws}경기 (확률: {round(draws/total_matches*100, 1)}%)")
    print("-" * 50)
    print("🤖 AI 인사이트: 예측 모델을 만들 때, 아무 정보가 없어도 홈팀에게 이 확률만큼 기본 가중치를 주어야 합니다!")

else:
    print(f"❌ 데이터를 불러오지 못했습니다. 에러 코드: {response.status_code}")
