import httpx
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from .config import config
from .auth_manager import AuthManager

class OutlookClient:
    def __init__(self):
        self.auth_manager = AuthManager()
        self.graph_endpoint = config.GRAPH_API_ENDPOINT

    async def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Graph API 요청 실행"""
        token = await self.auth_manager.get_valid_token()
        if not token:
            raise Exception("인증되지 않음. 먼저 로그인하세요.")

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        url = f"{self.graph_endpoint}{endpoint}"

        async with httpx.AsyncClient() as client:
            if method.upper() == "GET":
                response = await client.get(url, headers=headers)
            elif method.upper() == "POST":
                response = await client.post(url, headers=headers, json=data)
            elif method.upper() == "DELETE":
                response = await client.delete(url, headers=headers)
            elif method.upper() == "PATCH":
                response = await client.patch(url, headers=headers, json=data)
            else:
                raise ValueError(f"지원하지 않는 HTTP 메서드: {method}")

            response.raise_for_status()

            # DELETE 요청의 경우 빈 응답이 올 수 있음
            if response.status_code == 204:
                return {"success": True}

            return response.json()

    async def get_events(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[Dict[str, Any]]:
        """일정 조회"""
        endpoint = "/me/events"

        # 날짜 필터 추가
        if start_date or end_date:
            filters = []
            if start_date:
                filters.append(f"start/dateTime ge '{start_date}'")
            if end_date:
                filters.append(f"end/dateTime le '{end_date}'")
            endpoint += f"?$filter={' and '.join(filters)}"

        response = await self._make_request("GET", endpoint)
        return response.get("value", [])

    async def create_event(self, subject: str, start_time: str, end_time: str,
                          body: Optional[str] = None, location: Optional[str] = None,
                          attendees: Optional[List[str]] = None) -> Dict[str, Any]:
        """일정 생성"""
        event_data = {
            "subject": subject,
            "start": {
                "dateTime": start_time,
                "timeZone": "UTC"
            },
            "end": {
                "dateTime": end_time,
                "timeZone": "UTC"
            }
        }

        if body:
            event_data["body"] = {
                "contentType": "text",
                "content": body
            }

        if location:
            event_data["location"] = {
                "displayName": location
            }

        if attendees:
            event_data["attendees"] = [
                {
                    "emailAddress": {
                        "address": email,
                        "name": email
                    },
                    "type": "required"
                } for email in attendees
            ]

        return await self._make_request("POST", "/me/events", event_data)

    async def delete_event(self, event_id: str) -> Dict[str, Any]:
        """일정 삭제"""
        endpoint = f"/me/events/{event_id}"
        return await self._make_request("DELETE", endpoint)

    async def update_event(self, event_id: str, **kwargs) -> Dict[str, Any]:
        """일정 수정"""
        endpoint = f"/me/events/{event_id}"

        update_data = {}

        if "subject" in kwargs:
            update_data["subject"] = kwargs["subject"]

        if "start_time" in kwargs:
            update_data["start"] = {
                "dateTime": kwargs["start_time"],
                "timeZone": "UTC"
            }

        if "end_time" in kwargs:
            update_data["end"] = {
                "dateTime": kwargs["end_time"],
                "timeZone": "UTC"
            }

        if "body" in kwargs:
            update_data["body"] = {
                "contentType": "text",
                "content": kwargs["body"]
            }

        if "location" in kwargs:
            update_data["location"] = {
                "displayName": kwargs["location"]
            }

        return await self._make_request("PATCH", endpoint, update_data)

    async def get_user_info(self) -> Dict[str, Any]:
        """사용자 정보 조회"""
        return await self._make_request("GET", "/me")