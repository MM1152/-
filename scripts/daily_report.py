import os
import datetime
from github import Github
from notion_client import Client

# ⚠️ 여기를 본인 정보로 수정하세요
NOTION_DB_ID = "2a31ff657f5880898d15000cf8e24441"  # 하이픈 제거된 32자리 ID
TEAM_NAME = "12팀 (정상진, 천민성)"
GITHUB_USERNAME = "MM1152"  # 본인 GitHub 사용자명

def main():
    # 현재 날짜 (한국 시간 기준)
    kst = datetime.timezone(datetime.timedelta(hours=9))
    now = datetime.datetime.now(kst)
    today = now.strftime("%Y-%m-%d")
    
    print(f"📅 {today} 일간보고를 생성합니다...")
    
    # GitHub API 초기화
    github = Github(os.environ["GITHUB_TOKEN"])
    
    print("📋 GitHub 이슈를 가져오는 중...")
    
    # 최근 7일간의 이슈들만 확인
    seven_days_ago = now - datetime.timedelta(days=7)
    seven_days_ago_str = seven_days_ago.strftime("%Y-%m-%d")
    
    completed_issues = []
    incomplete_issues = []
    
    try:
        # 내가 작성한 이슈들 검색 
