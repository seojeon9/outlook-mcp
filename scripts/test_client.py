#!/usr/bin/env python3
"""
MCP 서버 테스트용 클라이언트
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import asyncio
import json
from datetime import datetime, timedelta
from src.outlook_client import OutlookClient
from src.auth_manager import AuthManager

async def test_outlook_client():
    """Outlook 클라이언트 기능 테스트"""
    auth_manager = AuthManager()
    outlook_client = OutlookClient()

    print("=== Outlook Calendar MCP Server 테스트 ===\n")

    # 인증 상태 확인
    is_authenticated = await auth_manager.is_authenticated()
    print(f"인증 상태: {'인증됨' if is_authenticated else '인증 필요'}")

    if not is_authenticated:
        print("먼저 인증을 완료해주세요:")
        print("1. uv run outlook-mcp (통합 서버 실행)")
        print("2. 브라우저에서 http://localhost:8000/auth/login 방문")
        print("3. Microsoft 계정으로 인증 완료")
        return

    try:
        # 사용자 정보 조회
        print("\n1. 사용자 정보 조회")
        user_info = await outlook_client.get_user_info()
        print(f"사용자: {user_info.get('displayName', 'N/A')}")
        print(f"이메일: {user_info.get('mail', user_info.get('userPrincipalName', 'N/A'))}")

        # 현재 일정 조회
        print("\n2. 현재 일정 조회")
        events = await outlook_client.get_events()
        print(f"총 {len(events)}개의 일정이 있습니다.")

        if events:
            print("\n최근 일정 3개:")
            for i, event in enumerate(events[:3]):
                print(f"{i+1}. {event.get('subject', '제목 없음')}")
                print(f"   시작: {event.get('start', {}).get('dateTime', 'N/A')}")
                print(f"   종료: {event.get('end', {}).get('dateTime', 'N/A')}")
                print(f"   ID: {event.get('id', 'N/A')}")
                print()

        # 테스트 일정 생성
        print("\n3. 테스트 일정 생성")
        tomorrow = datetime.now() + timedelta(days=1)
        start_time = tomorrow.replace(hour=10, minute=0, second=0, microsecond=0)
        end_time = start_time + timedelta(hours=1)

        test_event = await outlook_client.create_event(
            subject="MCP Server 테스트 일정",
            start_time=start_time.isoformat() + "Z",
            end_time=end_time.isoformat() + "Z",
            body="이 일정은 MCP 서버 테스트용으로 생성되었습니다.",
            location="테스트 장소"
        )

        event_id = test_event.get('id')
        print(f"테스트 일정이 생성되었습니다. ID: {event_id}")

        # 일정 수정
        print("\n4. 일정 수정 테스트")
        updated_event = await outlook_client.update_event(
            event_id,
            subject="[수정됨] MCP Server 테스트 일정",
            body="이 일정은 수정되었습니다."
        )
        print("일정이 수정되었습니다.")

        # 생성된 테스트 일정 삭제 여부 묻기
        print("\n5. 테스트 일정 삭제")
        response = input("생성된 테스트 일정을 삭제하시겠습니까? (y/N): ")
        if response.lower() == 'y':
            await outlook_client.delete_event(event_id)
            print("테스트 일정이 삭제되었습니다.")
        else:
            print("테스트 일정을 유지합니다.")

        print("\n=== 테스트 완료 ===")

    except Exception as e:
        print(f"오류 발생: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_outlook_client())