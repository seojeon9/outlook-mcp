FROM python:3.11-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 패키지 업데이트 및 필수 패키지 설치
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# UV 설치
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# 프로젝트 파일 복사
COPY pyproject.toml requirements.txt ./
COPY src/ ./src/
COPY scripts/ ./scripts/
COPY env_example.txt ./

# 의존성 설치
RUN uv sync --python=3.11 --prerelease=allow

# 환경 변수 기본값 설정
ENV HOST=0.0.0.0
ENV PORT=8000
ENV REDIRECT_URI=http://localhost:8000/auth/callback

# 포트 노출
EXPOSE 8000

# MCP 서버 실행
CMD ["uv", "run", "outlook-mcp"]