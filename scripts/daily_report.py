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
        # 내가 작성한 이슈들 검색 (전체 GitHub에서)
        created_query = f"author:{GITHUB_USERNAME} updated:>={seven_days_ago_str}"
        created_issues = github.search_issues(query=created_query)
        
        # 내가 할당받은 이슈들 검색
        assigned_query = f"assignee:{GITHUB_USERNAME} updated:>={seven_days_ago_str}"
        assigned_issues = github.search_issues(query=assigned_query)
        
        # 이슈들을 합치고 중복 제거
        all_issues = {}
        
        for issue in created_issues:
            all_issues[issue.number] = issue
        
        for issue in assigned_issues:
            all_issues[issue.number] = issue
        
        # 완료/미완료 분류
        for issue in all_issues.values():
            if issue.state == 'closed' and len(completed_issues) < 5:
                completed_issues.append(issue)
            elif issue.state == 'open' and len(incomplete_issues) < 5:
                incomplete_issues.append(issue)
        
        print(f"✅ 완료된 이슈: {len(completed_issues)}개")
        print(f"🔄 진행중 이슈: {len(incomplete_issues)}개")
        
    except Exception as e:
        print(f"⚠️ 이슈 검색 중 오류 (계속 진행): {e}")
    
    # 보고서 내용 생성
    report_content = f"""# {today} 일간보고: {TEAM_NAME}

# 이슈

---

# 전일 보고

## 완료
"""
    
    if completed_issues:
        for issue in completed_issues:
            report_content += f"- {issue.title} (#{issue.number})\n"
    else:
        report_content += "- 완료된 이슈 없음\n"
    
    report_content += """
## 미완료 (사유, 처리)
"""
    
    if incomplete_issues:
        for issue in incomplete_issues:
            report_content += f"- {issue.title} (#{issue.number}) - 진행중\n"
    else:
        report_content += "- 미완료 이슈 없음\n"
    
    report_content += """

---

# 금일 보고
- 오늘 진행할 작업을 여기에 기록해주세요
- 이 부분은 수동으로 업데이트가 필요합니다
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
                                "content": f"{today} 일간보고"
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
        
    except Exception as e:
        print(f"❌ Notion 저장 중 오류 발생: {e}")
        raise

if __name__ == "__main__":
    main()
