import requests
import os

# 1. API 키 설정
API_TOKEN = os.environ.get('FOOTBALL_API_TOKEN')
headers = {'X-Auth-Token': API_TOKEN}

# 2. 데이터 가져오기
url = 'https://api.football-data.org/v4/competitions/PL/matches?status=FINISHED'
response = requests.get(url, headers=headers)

if response.status_code == 200:
    data = response.json()
    matches = data.get('matches', [])
    
    # 💡 분석하고 싶은 팀 이름을 정확히 적습니다. (예: Manchester City FC, Arsenal FC, Tottenham Hotspur FC)
    TARGET_TEAM = "Manchester City FC"
    
    team_matches = 0
    wins = 0
    draws = 0
    losses = 0

    # 3. 전체 경기 중에서 TARGET_TEAM이 뛴 경기만 찾아서 분석합니다.
    for match in matches:
        home_team = match['homeTeam']['name']
        away_team = match['awayTeam']['name']
        winner = match['score']['winner']

        # 우리 팀이 홈에서 뛰었을 때
        if home_team == TARGET_TEAM:
            team_matches += 1
            if winner == 'HOME_TEAM': wins += 1
            elif winner == 'DRAW': draws += 1
            else: losses += 1
            
        # 우리 팀이 원정에서 뛰었을 때
        elif away_team == TARGET_TEAM:
            team_matches += 1
            if winner == 'AWAY_TEAM': wins += 1
            elif winner == 'DRAW': draws += 1
            else: losses += 1

    # 4. 분석 결과 출력
    print(f"⚽ [{TARGET_TEAM}] 23/24 시즌 정밀 분석 ⚽\n")
    print(f"📊 총 치른 경기: {team_matches}경기")
    print(f"✅ 승리: {wins}경기 (승률: {round(wins/team_matches*100, 1)}%)")
    print(f"🤝 무승부: {draws}경기")
    print(f"❌ 패배: {losses}경기")
    print("-" * 50)
    print("🤖 AI 예측 엔진: 이 데이터를 기반으로 다음 시즌 이 팀의 기본 승리 확률을 설정합니다.")

else:
    print(f"❌ 데이터를 불러오지 못했습니다. 에러 코드: {response.status_code}")
