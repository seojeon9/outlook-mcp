# Azure Entra ID 설정 가이드

Microsoft Graph API 사용을 위한 Azure Entra ID(AD) 애플리케이션 등록 방법입니다.

### 단계별 설정

1. **Azure Portal 접속**
   - https://portal.azure.com/ 에 로그인
   - Azure Active Directory 서비스로 이동

2. **애플리케이션 등록**
   - 좌측 메뉴에서 "App registrations" 클릭
   - "New registration" 버튼 클릭

3. **애플리케이션 정보 입력**
   - Name: `Outlook Calendar MCP Server` (또는 원하는 이름)
   - Supported account types:
     - "Accounts in any organizational directory and personal Microsoft accounts (Personal Microsoft accounts - e.g. Skype, Xbox)" 선택
   - Redirect URI:
     - Platform: Web
     - URI: `http://localhost:8000/auth/callback`
   - "Register" 버튼 클릭

4. **클라이언트 정보 복사**
   - 생성된 애플리케이션의 "Overview" 페이지에서
   - "Application (client) ID" 값을 복사해두세요

5. **클라이언트 시크릿 생성**
   - 좌측 메뉴에서 "Certificates & secrets" 클릭
   - "Client secrets" 탭에서 "New client secret" 클릭
   - Description: `MCP Server Secret`
   - Expires: 24 months (권장)
   - "Add" 버튼 클릭
   - 생성된 Value를 즉시 복사해두세요 (나중에 다시 볼 수 없습니다!)

6. **API 권한 설정**
   - 좌측 메뉴에서 "API permissions" 클릭
   - "Add a permission" 버튼 클릭
   - "Microsoft Graph" 선택
   - "Delegated permissions" 선택
   - 다음 권한들을 검색하여 추가:
     - `Calendars.ReadWrite` (캘린더 읽기/쓰기)
     - `User.Read` (사용자 기본 정보 읽기)
   - "Add permissions" 버튼 클릭

## 환경 변수 설정

`.env` 파일을 생성하고 Azure AD 정보를 입력하세요:

```bash
cp env_example.txt .env
```

```env
AZURE_CLIENT_ID=위에서_복사한_Application_ID
AZURE_CLIENT_SECRET=위에서_복사한_Client_Secret
AZURE_TENANT_ID=common
```
