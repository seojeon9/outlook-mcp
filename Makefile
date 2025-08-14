# Outlook Calendar MCP Server Makefile

.PHONY: install dev auth server test clean format lint help

# 기본 타겟
help:
	@echo "사용 가능한 명령어:"
	@echo "  install     - 의존성 설치"
	@echo "  check-env   - 환경 변수 확인"
	@echo "  auth        - OAuth 인증 서버 실행"
	@echo "  server      - MCP 서버 실행"
	@echo "  web         - 통합 웹 서버 실행"
	@echo "  test        - 테스트 클라이언트 실행"
	@echo "  clean       - 캐시 및 임시 파일 삭제"
	@echo "  reset       - UV 환경 재생성"

# 의존성 설치
install:
	uv sync --python=3.11 --prerelease=allow

# 개발 의존성까지 설치
dev:
	uv sync --python=3.11 --prerelease=allow

# OAuth 인증 서버 실행
auth:
	uv run outlook-auth

# MCP 서버 실행
server:
	uv run outlook-mcp

# 웹 서버 모드로 실행 (OAuth + MCP)
web:
	uv run python -m src.mcp_server web

# 테스트 클라이언트 실행
test:
	uv run python scripts/test_client.py

# 환경 변수 확인
check-env:
	uv run python scripts/check_env.py

# 코드 포맷팅 (개발 도구가 설치된 경우에만)
format:
	@echo "코드 포맷팅 도구가 필요하면 별도 설치하세요"

# 코드 린팅 (개발 도구가 설치된 경우에만)
lint:
	@echo "코드 린팅 도구가 필요하면 별도 설치하세요"

# 린팅 문제 자동 수정
lint-fix:
	@echo "코드 린팅 도구가 필요하면 별도 설치하세요"

# 캐시 및 임시 파일 삭제
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name ".pytest_cache" -delete
	rm -rf .ruff_cache
	rm -f token.json

# 환경 변수 파일 생성
setup-env:
	cp env_example.txt .env
	@echo ".env 파일이 생성되었습니다. Azure AD 정보를 입력하세요."

# 전체 설정 (처음 실행시)
setup: setup-env install
	@echo "설정이 완료되었습니다!"
	@echo "1. .env 파일에 Azure AD 정보를 입력하세요"
	@echo "2. 'make auth'로 인증을 완료하세요"
	@echo "3. 'make server'로 MCP 서버를 실행하세요"

# UV 초기화 (문제 발생시)
reset:
	rm -rf .venv
	uv sync --python=3.11 --prerelease=allow