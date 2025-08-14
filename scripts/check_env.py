#!/usr/bin/env python3
"""
환경 변수 확인 스크립트
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.config import config

def check_environment():
    """환경 변수 상태 확인"""
    print("=== 환경 변수 확인 ===\n")

    # Azure AD 설정
    print("Azure AD 설정:")
    print(f"AZURE_CLIENT_ID: {'✅ 설정됨' if config.AZURE_CLIENT_ID else '❌ 설정되지 않음'}")
    if config.AZURE_CLIENT_ID:
        print(f"  값: {config.AZURE_CLIENT_ID[:8]}...")

    print(f"AZURE_CLIENT_SECRET: {'✅ 설정됨' if config.AZURE_CLIENT_SECRET else '❌ 설정되지 않음'}")
    if config.AZURE_CLIENT_SECRET:
        print(f"  값: {'*' * 8}...")

    print(f"AZURE_TENANT_ID: {config.AZURE_TENANT_ID}")

    # OAuth 설정
    print(f"\nOAuth 설정:")
    print(f"REDIRECT_URI: {config.REDIRECT_URI}")
    print(f"SCOPES: {config.SCOPES}")

    # 서버 설정
    print(f"\n서버 설정:")
    print(f"HOST: {config.HOST}")
    print(f"PORT: {config.PORT}")
    print(f"TOKEN_FILE: {config.TOKEN_FILE}")

    # Graph API
    print(f"\nMicrosoft Graph:")
    print(f"GRAPH_API_ENDPOINT: {config.GRAPH_API_ENDPOINT}")
    print(f"AUTHORITY: {config.AUTHORITY}")

    # .env 파일 확인
    env_file = ".env"
    if os.path.exists(env_file):
        print(f"\n✅ .env 파일이 존재합니다.")
    else:
        print(f"\n❌ .env 파일이 없습니다.")
        print("env_example.txt를 .env로 복사하고 설정하세요:")
        print("cp env_example.txt .env")

    # 필수 설정 확인
    missing = []
    if not config.AZURE_CLIENT_ID:
        missing.append("AZURE_CLIENT_ID")
    if not config.AZURE_CLIENT_SECRET:
        missing.append("AZURE_CLIENT_SECRET")

    if missing:
        print(f"\n❌ 누락된 필수 환경 변수: {', '.join(missing)}")
        print("Azure Portal에서 애플리케이션을 등록하고 .env 파일에 설정하세요.")
        return False
    else:
        print(f"\n✅ 모든 필수 환경 변수가 설정되었습니다.")
        return True

if __name__ == "__main__":
    success = check_environment()
    if not success:
        print(f"\n📚 설정 가이드: docs/setup_guide.md")
        sys.exit(1)
    else:
        print(f"\n🚀 준비 완료! 이제 'make auth'로 인증 서버를 시작하세요.")