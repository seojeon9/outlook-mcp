import json
import os
import time
import httpx
import secrets
import base64
from urllib.parse import urlencode, parse_qs
from typing import Optional, Dict, Any
from .config import config

class AuthManager:
    def __init__(self):
        self.token_file = config.TOKEN_FILE
        self.client_id = config.AZURE_CLIENT_ID
        self.client_secret = config.AZURE_CLIENT_SECRET
        self.redirect_uri = config.REDIRECT_URI
        self.scopes = " ".join(config.SCOPES)
        self.authority = config.AUTHORITY

    def get_authorization_url(self) -> tuple[str, str]:
        """OAuth 인증 URL 생성"""
        state = secrets.token_urlsafe(32)

        params = {
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": self.redirect_uri,
            "scope": self.scopes,
            "state": state,
            "response_mode": "query"
        }

        auth_url = f"{self.authority}/oauth2/v2.0/authorize?" + urlencode(params)
        return auth_url, state

    async def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """인증 코드를 액세스 토큰으로 교환"""
        # 환경 변수 확인
        if not self.client_id:
            raise ValueError("AZURE_CLIENT_ID 환경 변수가 설정되지 않았습니다.")
        if not self.client_secret:
            raise ValueError("AZURE_CLIENT_SECRET 환경 변수가 설정되지 않았습니다.")

        token_url = f"{self.authority}/oauth2/v2.0/token"

        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": self.redirect_uri,
            "scope": self.scopes
        }

        print(f"토큰 요청 URL: {token_url}")
        print(f"클라이언트 ID: {self.client_id[:8] if self.client_id else 'None'}...")

        async with httpx.AsyncClient() as client:
            response = await client.post(token_url, data=data)
            if response.status_code != 200:
                print(f"에러 응답: {response.status_code}")
                print(f"에러 내용: {response.text}")
            response.raise_for_status()
            token_data = response.json()

        # 토큰 만료 시간 계산
        token_data['expires_at'] = time.time() + token_data.get('expires_in', 3600)

        # 토큰 저장
        await self.save_token(token_data)
        return token_data

    async def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """리프레시 토큰을 사용하여 새 액세스 토큰 획득"""
        token_url = f"{self.authority}/oauth2/v2.0/token"

        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
            "scope": self.scopes
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(token_url, data=data)
            response.raise_for_status()
            token_data = response.json()

        token_data['expires_at'] = time.time() + token_data.get('expires_in', 3600)
        await self.save_token(token_data)
        return token_data

    async def get_valid_token(self) -> Optional[str]:
        """유효한 액세스 토큰 반환"""
        token_data = await self.load_token()
        if not token_data:
            return None

        # 토큰이 만료되었는지 확인
        if time.time() >= token_data.get('expires_at', 0):
            if 'refresh_token' in token_data:
                try:
                    token_data = await self.refresh_token(token_data['refresh_token'])
                except Exception:
                    return None
            else:
                return None

        return token_data.get('access_token')

    async def save_token(self, token_data: Dict[str, Any]):
        """토큰을 파일에 저장"""
        with open(self.token_file, 'w') as f:
            json.dump(token_data, f, indent=2)

    async def load_token(self) -> Optional[Dict[str, Any]]:
        """파일에서 토큰 로드"""
        if not os.path.exists(self.token_file):
            return None

        try:
            with open(self.token_file, 'r') as f:
                return json.load(f)
        except Exception:
            return None

    async def is_authenticated(self) -> bool:
        """인증 상태 확인"""
        token = await self.get_valid_token()
        return token is not None

    async def clear_token(self):
        """저장된 토큰 삭제"""
        if os.path.exists(self.token_file):
            os.remove(self.token_file)