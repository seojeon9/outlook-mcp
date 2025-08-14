# Outlook Calendar MCP Server

[![smithery badge](https://smithery.ai/badge/@seojeon9/outlook-mcp)](https://smithery.ai/server/@seojeon9/outlook-mcp)

Outlook/Microsoft 365 캘린더를 MCP(Model Context Protocol)로 연결해,
에이전트가 일정 조회/생성/수정/삭제를 자동화합니다.
> Acknowledgements: 본 초기 버전은 바이브코딩으로 빠르게 프로토타이핑되었습니다.

## 빠른 시작

```bash
# 1. 의존성 설치
uv sync --python=3.11 --prerelease=allow

# 2. 환경 변수 설정
cp env_example.txt .env
# .env 파일에 Azure AD 정보 입력

# 3. 서버 실행
uv run outlook-mcp
```

## 기능

- 일정 조회/생성/수정/삭제
- Microsoft 계정 OAuth 인증
- Claude Desktop 통합 지원

## Claude Desktop에 추가

Claude Desktop 설정 파일에 추가:

```json
{
  "mcpServers": {
    "outlook-calendar": {
      "command": "uv",
      "args": ["run", "outlook-mcp"],
      "cwd": "/path/to/your/outlook_mcp"
    }
  }
}
```

**설정 파일 위치:**
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`

### Installing via Smithery

To install Outlook Calendar for Claude Desktop automatically via [Smithery](https://smithery.ai/server/@seojeon9/outlook-mcp):

```bash
npx -y @smithery/cli install @seojeon9/outlook-mcp --client claude
```

## 사용 예시

Claude에서 다음과 같이 사용:

```
내 이번 주 일정을 보여주세요
내일 오후 2시에 팀 회의 일정을 추가해주세요
```

## 📁 프로젝트 구조

```
outlook_mcp/
├── src/                   # 핵심 라이브러리
│   ├── mcp_server.py       # MCP + FastAPI 통합 서버
│   ├── auth_manager.py     # OAuth 인증 관리
│   ├── outlook_client.py   # Microsoft Graph API 클라이언트
│   └── config.py           # 설정 관리
├── scripts/               # 유틸리티 도구
│   ├── check_env.py        # 환경 변수 확인
│   └── test_client.py      # 기능 테스트
└── docs/                  # 문서
    ├── azure_ad_setup.md   # Azure AD 설정 가이드
    └── claude_setup.md     # Claude Desktop 설정
```

## 문서

- [Azure AD 설정 가이드](docs/azure_ad_setup.md)
- [Claude Desktop 설정](docs/claude_setup.md)