import os
import datetime
from github import Github
from notion_client import Client

# ⚠️ 여기를 본인 정보로 수정하세요
NOTION_DB_ID = "2a31ff65-7f58-80ef-9cd8-cac9ad2a7c19"
TEAM_NAME = "12팀 (정상진, 천민성)"
GITHUB_USERNAME = "MM1152"  # 본인 GitHub 사용자명

def main():
    # 현재 날짜 (한국 시간 기준)
    kst = datetime.timezone(datetime.timedelta(hours=9))
    now = datetime.datetime.now(kst)
    today = now.strftime("%Y-%m-%d")
    yesterday = (now - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    
    print(f"📅 {today} 일간보고를 생성합니다...")
    print(f"📅 전날: {yesterday}")
    
    # GitHub API 초기화
    github = Github(os.environ["GITHUB_TOKEN"])
    
    print("📋 GitHub 이슈를 가져오는 중...")
    
    yesterday_completed_issues = []
    today_open_issues = []
    
    try:
        # 전날 완료된 이슈들 검색 (정확히 어제 닫힌 이슈)
        yesterday_closed_query = f"author:{GITHUB_USERNAME} closed:{yesterday}"
        yesterday_closed_by_author = github.search_issues(query=yesterday_closed_query)
        
        yesterday_assigned_closed_query = f"assignee:{GITHUB_USERNAME} closed:{yesterday}"
        yesterday_closed_by_assignee = github.search_issues(query=yesterday_assigned_closed_query)
        
        # 오늘 진행할 작업들 (열린 이슈 중 최근 업데이트된 것들)
        today_open_query = f"author:{GITHUB_USERNAME} state:open updated:>={yesterday}"
        today_open_by_author = github.search_issues(query=today_open_query)
        
        today_assigned_open_query = f"assignee:{GITHUB_USERNAME} state:open updated:>={yesterday}"
        today_open_by_assignee = github.search_issues(query=today_assigned_open_query)
        
        # 전날 완료된 이슈들 수집 (중복 제거)
        yesterday_issues = {}
        for issue in yesterday_closed_by_author:
            yesterday_issues[issue.number] = issue
        for issue in yesterday_closed_by_assignee:
            yesterday_issues[issue.number] = issue
        
        yesterday_completed_issues = list(yesterday_issues.values())[:5]  # 최대 5개
        
        # 오늘 진행할 이슈들 수집 (중복 제거)
        today_issues = {}
        for issue in today_open_by_author:
            today_issues[issue.number] = issue
        for issue in today_open_by_assignee:
            today_issues[issue.number] = issue
        
        today_open_issues = list(today_issues.values())[:5]  # 최대 5개
        
        print(f"✅ 전날({yesterday}) 완료된 이슈: {len(yesterday_completed_issues)}개")
        print(f"🔄 오늘({today}) 진행할 이슈: {len(today_open_issues)}개")
        
    except Exception as e:
        print(f"⚠️ 이슈 검색 중 오류 (계속 진행): {e}")
    
    # 보고서 내용 생성
    report_content = f"""# {today} 일간보고: {TEAM_NAME}

## 📊 이슈 현황
- 전날 완료: {len(yesterday_completed_issues)}개
- 금일 진행: {len(today_open_issues)}개

---

## 📋 전일({yesterday}) 보고

### ✅ 완료
"""
    
    if yesterday_completed_issues:
        for issue in yesterday_completed_issues:
            # 이슈가 속한 레포지토리 정보 추가
            repo_name = issue.repository.full_name if hasattr(issue, 'repository') else "Unknown"
            closed_time = issue.closed_at.strftime("%H:%M") if issue.closed_at else ""
            report_content += f"- **{issue.title}** (#{issue.number}) - {repo_name}"
            if closed_time:
                report_content += f" `완료시간: {closed_time}`"
            report_content += f"\n  - 링크: {issue.html_url}\n"
    else:
        report_content += "- 완료된 이슈 없음\n"
    
    report_content += f"""
### ❌ 미완료 (사유, 처리계획)
"""
    
    # 어제부터 오늘까지 미완료된 이슈들 찾기
    uncompleted_issues = []
    try:
        uncompleted_query = f"assignee:{GITHUB_USERNAME} state:open updated:<{today} updated:>={yesterday}"
        uncompleted_search = github.search_issues(query=uncompleted_query)
        uncompleted_issues = list(uncompleted_search)[:3]  # 최대 3개
    except:
        pass
    
    if uncompleted_issues:
        for issue in uncompleted_issues:
            repo_name = issue.repository.full_name if hasattr(issue, 'repository') else "Unknown"
            report_content += f"- **{issue.title}** (#{issue.number}) - {repo_name}\n"
            report_content += f"  - 사유: 진행중\n"
            report_content += f"  - 처리계획: 금일 완료 예정\n"
    else:
        report_content += "- 미완료 이슈 없음\n"
    
    report_content += f"""

---

## 🎯 금일({today}) 보고

### 📝 계획된 작업
"""
    
    if today_open_issues:
        for issue in today_open_issues:
            repo_name = issue.repository.full_name if hasattr(issue, 'repository') else "Unknown"
            labels = ", ".join([label.name for label in issue.labels]) if issue.labels else "라벨 없음"
            report_content += f"- **{issue.title}** (#{issue.number}) - {repo_name}\n"
            report_content += f"  - 라벨: {labels}\n"
            report_content += f"  - 링크: {issue.html_url}\n"
    else:
        report_content += "- 할당된 이슈 없음\n"
    
    # 추가 계획 섹션
    report_content += f"""
### 💡 추가 작업 계획
- 새로운 기능 개발 검토
- 코드 리뷰 및 테스트
- 문서 업데이트

### 🚧 블로커/이슈
- 현재 특별한 블로커 없음

---

## 📈 진행 상황
**어제 완료율**: {len(yesterday_completed_issues)}/5 이슈
**오늘 목표**: {len(today_open_issues)} 이슈 진행

*생성 시간: {now.strftime("%Y-%m-%d %H:%M:%S")} (KST)*
"""
    
    print("📝 보고서 내용 생성 완료")
    
    # Notion에 저장
    print("📤 Notion에 저장하는 중...")
    
    notion = Client(auth=os.environ["NOTION_TOKEN"])
    
    try:
        new_page = notion.pages.create(
            parent={"database_id": NOTION_DB_ID},
            properties={
                "제목": {
                    "title": [
                        {
                            "text": {
                                "content": f"📊 {today} 일간보고 - {TEAM_NAME}"
                            }
                        }
                    ]
                },
                "작성일": {
                    "date": {
                        "start": today
                    }
                }
            },
            children=[
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": report_content
                                }
                            }
                        ]
                    }
                }
            ]
        )
        
        print("✅ 일간보고가 성공적으로 Notion에 저장되었습니다!")
        print(f"📄 페이지 ID: {new_page['id']}")
        print(f"📊 전날 완료: {len(yesterday_completed_issues)}개, 금일 진행: {len(today_open_issues)}개")
        
    except Exception as e:
        print(f"❌ Notion 저장 중 오류 발생: {e}")
        raise

if __name__ == "__main__":
    main()
