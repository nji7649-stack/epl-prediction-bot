import requests
import os

API_TOKEN = os.environ.get('FOOTBALL_API_TOKEN')
headers = {'X-Auth-Token': API_TOKEN}

url = 'https://api.football-data.org/v4/competitions/PL/matches?status=FINISHED'
response = requests.get(url, headers=headers)

if response.status_code == 200:
    data = response.json()
    matches = data.get('matches', [])
    
    # 💡 이름이 조금 달라도 찾을 수 있게 핵심 단어만 넣습니다!
    TARGET_TEAM = "Manchester City"
    
    team_matches = 0
    wins = 0
    draws = 0
    losses = 0

    # 'in'을 사용해서 팀 이름에 "Manchester City"가 포함만 되어 있으면 찾아냅니다.
    for match in matches:
        home_team = match['homeTeam']['name']
        away_team = match['awayTeam']['name']
        winner = match['score']['winner']

        if TARGET_TEAM in home_team:
            team_matches += 1
            if winner == 'HOME_TEAM': wins += 1
            elif winner == 'DRAW': draws += 1
            else: losses += 1
            
        elif TARGET_TEAM in away_team:
            team_matches += 1
            if winner == 'AWAY_TEAM': wins += 1
            elif winner == 'DRAW': draws += 1
            else: losses += 1

    print(f"⚽ [{TARGET_TEAM}] 최근 종료된 시즌 정밀 분석 ⚽\n")
    
    # 0경기일 때 뻗지 않도록 방어막(예외 처리)을 쳐줍니다.
    if team_matches == 0:
        print("❌ 팀을 찾을 수 없습니다. 스펠링을 다시 확인해주세요.")
        print(f"💡 힌트: 실제 데이터에 등록된 팀 이름 예시 -> {matches[0]['homeTeam']['name']}, {matches[1]['homeTeam']['name']}")
    else:
        print(f"📊 총 치른 경기: {team_matches}경기")
        print(f"✅ 승리: {wins}경기 (승률: {round(wins/team_matches*100, 1)}%)")
        print(f"🤝 무승부: {draws}경기")
        print(f"❌ 패배: {losses}경기")
        print("-" * 50)
        print("🤖 AI 예측 엔진: 이 데이터를 기반으로 다음 시즌 이 팀의 기본 승리 확률을 설정합니다.")

else:
    print(f"❌ 데이터를 불러오지 못했습니다. 에러 코드: {response.status_code}")
