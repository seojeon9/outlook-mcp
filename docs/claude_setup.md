# Claude Desktop 설정

Claude Desktop에 MCP 서버를 추가하는 방법입니다.

## 🔧 설정 방법

## 설정 파일 위치

**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
**Linux:** `~/.config/Claude/claude_desktop_config.json`

## 설정 내용

Claude Desktop 설정 파일에 다음 내용을 추가:

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

**⚠️ `"cwd"`를 실제 프로젝트 경로로 변경하세요!**

## 사용법

1. Claude Desktop 재시작
2. 새 대화에서 "내 이번 주 일정을 보여주세요" 입력
3. 처음 사용시 인증이 필요하면 브라우저에서 http://localhost:8000/auth/login 방문