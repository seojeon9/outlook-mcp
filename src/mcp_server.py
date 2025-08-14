import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Sequence
import uvicorn
from fastapi import FastAPI, Request, HTTPException, Query
from fastapi.responses import HTMLResponse, RedirectResponse

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("outlook-mcp")

from mcp.server import Server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource
)

from .config import config
from .auth_manager import AuthManager
from .outlook_client import OutlookClient

# MCP 서버 초기화
logger.info("MCP 서버 초기화 중...")
mcp_server = Server("outlook-calendar")
auth_manager = AuthManager()
outlook_client = OutlookClient()
logger.info("MCP 서버 초기화 완료")

# FastAPI 앱 (OAuth callback용)
app = FastAPI(title="Outlook Calendar MCP Server")

# 전역 상태 저장용
auth_state = {}

@app.get("/")
async def root():
    """서버 상태 확인"""
    is_authenticated = await auth_manager.is_authenticated()
    return {
        "message": "Outlook Calendar MCP Server",
        "authenticated": is_authenticated,
        "auth_url": "/auth/login" if not is_authenticated else None
    }

@app.get("/auth/login")
async def login():
    """OAuth 로그인 시작"""
    logger.info("OAuth 로그인 시작")
    auth_url, state = auth_manager.get_authorization_url()
    auth_state[state] = True

    return HTMLResponse(f"""
    <html>
        <head><title>Outlook Calendar 인증</title></head>
        <body>
            <h1>Outlook Calendar 인증</h1>
            <p>아래 링크를 클릭하여 Microsoft 계정으로 로그인하세요:</p>
            <a href="{auth_url}" target="_blank">Microsoft 로그인</a>
        </body>
    </html>
    """)

@app.get("/auth/callback")
async def auth_callback(code: str = Query(...), state: str = Query(...)):
    """OAuth callback 처리"""
    logger.info(f"OAuth callback 받음: state={state}")
    if state not in auth_state:
        logger.error("잘못된 state 값")
        raise HTTPException(status_code=400, detail="잘못된 state 값")

    try:
        token_data = await auth_manager.exchange_code_for_token(code)
        del auth_state[state]
        logger.info("OAuth 인증 성공")

        return HTMLResponse("""
        <html>
            <head><title>인증 완료</title></head>
            <body>
                <h1>인증 완료!</h1>
                <p>성공적으로 인증되었습니다. 이제 창을 닫으셔도 됩니다.</p>
                <script>window.close();</script>
            </body>
        </html>
        """)
    except Exception as e:
        logger.error(f"OAuth 인증 실패: {str(e)}")
        raise HTTPException(status_code=400, detail=f"인증 실패: {str(e)}")

@app.get("/auth/logout")
async def logout():
    """로그아웃"""
    logger.info("로그아웃 요청")
    await auth_manager.clear_token()
    return {"message": "로그아웃되었습니다."}

# MCP 서버 도구 정의
@mcp_server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """사용 가능한 도구 목록 반환"""
    logger.info("도구 목록 요청됨")
    tools = [
        Tool(
            name="authenticate",
            description="Microsoft 계정으로 인증합니다.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="get_events",
            description="일정을 조회합니다.",
            inputSchema={
                "type": "object",
                "properties": {
                    "start_date": {
                        "type": "string",
                        "description": "시작 날짜 (ISO 8601 형식, 예: 2024-01-01T00:00:00Z)"
                    },
                    "end_date": {
                        "type": "string",
                        "description": "종료 날짜 (ISO 8601 형식, 예: 2024-01-31T23:59:59Z)"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="create_event",
            description="새 일정을 생성합니다.",
            inputSchema={
                "type": "object",
                "properties": {
                    "subject": {
                        "type": "string",
                        "description": "일정 제목"
                    },
                    "start_time": {
                        "type": "string",
                        "description": "시작 시간 (ISO 8601 형식, 예: 2024-01-01T10:00:00Z)"
                    },
                    "end_time": {
                        "type": "string",
                        "description": "종료 시간 (ISO 8601 형식, 예: 2024-01-01T11:00:00Z)"
                    },
                    "body": {
                        "type": "string",
                        "description": "일정 내용 (선택사항)"
                    },
                    "location": {
                        "type": "string",
                        "description": "장소 (선택사항)"
                    },
                    "attendees": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "참석자 이메일 목록 (선택사항)"
                    }
                },
                "required": ["subject", "start_time", "end_time"]
            }
        ),
        Tool(
            name="delete_event",
            description="일정을 삭제합니다.",
            inputSchema={
                "type": "object",
                "properties": {
                    "event_id": {
                        "type": "string",
                        "description": "삭제할 일정의 ID"
                    }
                },
                "required": ["event_id"]
            }
        ),
        Tool(
            name="update_event",
            description="일정을 수정합니다.",
            inputSchema={
                "type": "object",
                "properties": {
                    "event_id": {
                        "type": "string",
                        "description": "수정할 일정의 ID"
                    },
                    "subject": {
                        "type": "string",
                        "description": "일정 제목 (선택사항)"
                    },
                    "start_time": {
                        "type": "string",
                        "description": "시작 시간 (ISO 8601 형식, 선택사항)"
                    },
                    "end_time": {
                        "type": "string",
                        "description": "종료 시간 (ISO 8601 형식, 선택사항)"
                    },
                    "body": {
                        "type": "string",
                        "description": "일정 내용 (선택사항)"
                    },
                    "location": {
                        "type": "string",
                        "description": "장소 (선택사항)"
                    }
                },
                "required": ["event_id"]
            }
        ),
        Tool(
            name="get_user_info",
            description="현재 로그인한 사용자 정보를 조회합니다.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        )
    ]
    logger.info(f"총 {len(tools)}개의 도구 반환")
    return tools

@mcp_server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[TextContent | ImageContent | EmbeddedResource]:
    """도구 실행 처리"""
    logger.info(f"도구 실행 요청: {name}, 인자: {arguments}")
    try:
        if name == "authenticate":
            logger.info("인증 상태 확인 중...")
            is_authenticated = await auth_manager.is_authenticated()
            if is_authenticated:
                logger.info("이미 인증된 상태")
                user_info = await outlook_client.get_user_info()
                return [TextContent(
                    type="text",
                    text=f"이미 인증되어 있습니다. 사용자: {user_info.get('displayName', 'Unknown')}"
                )]
            else:
                logger.info("인증 필요")
                return [TextContent(
                    type="text",
                    text=f"인증이 필요합니다. 다음 URL을 방문하세요: http://{config.HOST}:{config.PORT}/auth/login"
                )]

        # 인증 확인
        if not await auth_manager.is_authenticated():
            logger.warning(f"인증되지 않은 상태에서 {name} 도구 실행 시도")
            return [TextContent(
                type="text",
                text=f"인증이 필요합니다. 먼저 authenticate 도구를 사용하거나 http://{config.HOST}:{config.PORT}/auth/login을 방문하세요."
            )]

        if name == "get_events":
            logger.info("일정 조회 시작")
            events = await outlook_client.get_events(
                start_date=arguments.get("start_date"),
                end_date=arguments.get("end_date")
            )
            logger.info(f"{len(events)}개의 일정 조회됨")

            if not events:
                return [TextContent(type="text", text="일정이 없습니다.")]

            result = "일정 목록:\n\n"
            for event in events:
                start = event.get("start", {}).get("dateTime", "시간 정보 없음")
                end = event.get("end", {}).get("dateTime", "시간 정보 없음")
                subject = event.get("subject", "제목 없음")
                location = event.get("location", {}).get("displayName", "")
                event_id = event.get("id", "")

                result += f"제목: {subject}\n"
                result += f"시작: {start}\n"
                result += f"종료: {end}\n"
                if location:
                    result += f"장소: {location}\n"
                result += f"ID: {event_id}\n"
                result += "-" * 50 + "\n"

            return [TextContent(type="text", text=result)]

        elif name == "create_event":
            logger.info(f"일정 생성 시작: {arguments['subject']}")
            event = await outlook_client.create_event(
                subject=arguments["subject"],
                start_time=arguments["start_time"],
                end_time=arguments["end_time"],
                body=arguments.get("body"),
                location=arguments.get("location"),
                attendees=arguments.get("attendees")
            )
            logger.info(f"일정 생성 완료: {event.get('id')}")

            return [TextContent(
                type="text",
                text=f"일정이 생성되었습니다.\n제목: {event.get('subject')}\nID: {event.get('id')}"
            )]

        elif name == "delete_event":
            logger.info(f"일정 삭제 시작: {arguments['event_id']}")
            await outlook_client.delete_event(arguments["event_id"])
            logger.info("일정 삭제 완료")
            return [TextContent(type="text", text="일정이 삭제되었습니다.")]

        elif name == "update_event":
            event_id = arguments.pop("event_id")
            logger.info(f"일정 수정 시작: {event_id}")
            event = await outlook_client.update_event(event_id, **arguments)
            logger.info("일정 수정 완료")
            return [TextContent(
                type="text",
                text=f"일정이 수정되었습니다.\n제목: {event.get('subject')}\nID: {event.get('id')}"
            )]

        elif name == "get_user_info":
            logger.info("사용자 정보 조회 시작")
            user_info = await outlook_client.get_user_info()
            result = f"사용자 정보:\n"
            result += f"이름: {user_info.get('displayName', 'N/A')}\n"
            result += f"이메일: {user_info.get('mail', user_info.get('userPrincipalName', 'N/A'))}\n"
            result += f"ID: {user_info.get('id', 'N/A')}"
            logger.info("사용자 정보 조회 완료")

            return [TextContent(type="text", text=result)]

        else:
            logger.warning(f"알 수 없는 도구: {name}")
            return [TextContent(type="text", text=f"알 수 없는 도구: {name}")]

    except Exception as e:
        logger.error(f"도구 실행 중 오류: {str(e)}")
        return [TextContent(type="text", text=f"오류 발생: {str(e)}")]

async def run_mcp_server():
    """MCP 서버 실행"""
    logger.info("MCP 서버 시작 중...")
    from mcp.server.stdio import stdio_server

    async with stdio_server() as (read_stream, write_stream):
        logger.info("MCP 서버가 stdio에서 실행 중입니다")
        await mcp_server.run(read_stream, write_stream, mcp_server.create_initialization_options())

async def run_integrated_server():
    """MCP 서버와 웹 서버를 동시에 실행"""
    logger.info("통합 서버 시작 중...")

    # 웹 서버를 백그라운드에서 실행
    import threading
    import uvicorn

    def start_web_server():
        logger.info(f"웹 서버 시작: http://{config.HOST}:{config.PORT}")
        uvicorn.run(app, host=config.HOST, port=config.PORT, log_level="warning")

    # 웹 서버를 별도 스레드에서 시작
    web_thread = threading.Thread(target=start_web_server, daemon=True)
    web_thread.start()

    # MCP 서버 실행
    await run_mcp_server()

def run_web_server():
    """웹 서버 실행 (OAuth callback용)"""
    logger.info(f"웹 서버 시작: http://{config.HOST}:{config.PORT}")
    uvicorn.run(app, host=config.HOST, port=config.PORT)

def main():
    """메인 엔트리포인트"""
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "web":
        # 웹 서버 전용 모드
        print(f"웹 서버 시작 중... http://{config.HOST}:{config.PORT}")
        run_web_server()
    else:
        # 통합 모드 (MCP + 웹 서버)
        logger.info("통합 서버 모드로 시작 (MCP + OAuth 웹서버)")
        asyncio.run(run_integrated_server())

if __name__ == "__main__":
    main()