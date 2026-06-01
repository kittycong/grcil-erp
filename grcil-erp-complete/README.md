# 구로ERP - 장애인 자립생활 지원 센터 전자결재 시스템

> **효율적인 인사관리, 함께하는 센터**
> 
> 20명 규모 사무실의 휴가관리, 급여계산, 보고서 생성을 한곳에서 처리하는 웹 기반 ERP 시스템

![GitHub License](https://img.shields.io/github/license/grcil/grcil-erp)
![Python Version](https://img.shields.io/badge/python-3.9%2B-blue)
![Version](https://img.shields.io/badge/version-0.9.0-blue)
![Status](https://img.shields.io/badge/status-Beta-yellow)

---

## 📋 주요 기능

### 👤 개인 모드
- ✅ 본인 휴가 현황 조회 (달력, 일수, 잔여일)
- ✅ 보상휴가(대체휴가) 관리
- ✅ 급여명세서 조회
- ✅ 개인 링크 공유

### 👥 관리자 모드
- ✅ 전사 직원 관리
- ✅ 휴가 승인/반려
- ✅ **HWPX 자동 파싱** (휴가신청서)
- ✅ **Excel 자동 동기화** (휴가현황, 직원정보)
- ✅ SQLite 중앙 데이터베이스
- ✅ 감시 로그 (감사 기록)
- ✅ 급여 계산 & 명세서 생성
- ✅ 보고서 생성 (HWP/PDF)

---

## 🚀 5분 안에 시작하기

### 1단계: 저장소 클론

```bash
git clone https://github.com/grcil/grcil-erp.git
cd grcil-erp
```

### 2단계: 환경 설정

```bash
# Python 3.9+ 필요
python --version

# 가상 환경 생성 (선택사항)
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 의존성 설치
pip install -r requirements.txt
```

### 3단계: 데이터베이스 초기화

```bash
python grcil_database.py

# 출력:
# ✅ 데이터베이스 초기화 완료: /home/user/.grcil_erp/grcil_erp.db
```

### 4단계: 백엔드 서버 실행

```bash
# 개발 모드 (Hot reload)
export FLASK_ENV=development
python app.py

# 또는 프로덕션 모드
gunicorn app:app --bind 0.0.0.0:5000
```

### 5단계: 프론트엔드 접속

**두 가지 방법 중 선택:**

**방법 A: 로컬 서버** (개발용)
```bash
# 별도 터미널에서
cd grcil-erp
python -m http.server 8091

# 브라우저: http://127.0.0.1:8091/grcil_erp_dashboard.html
```

**방법 B: GitHub Pages** (배포용)
```
https://grcil.github.io/grcil-erp/
```

---

## 🏗️ 아키텍처

```
┌─────────────────────────────────────────────────────┐
│             Frontend (HTML5/CSS3/JS)                │
│      grcil_erp_dashboard.html (프론트엔드)           │
│  - 개인/관리자 모드 분리                             │
│  - HWPX/Excel 드래그앤드롭 업로드                   │
│  - 실시간 데이터 표시                               │
└──────────────────┬──────────────────────────────────┘
                   │
                   │ REST API
                   │ (JSON)
                   ▼
┌─────────────────────────────────────────────────────┐
│          Backend (Python Flask)                     │
│            app.py (백엔드 API)                       │
│  ┌────────────────────────────────────────────┐    │
│  │  /api/parse/hwpx    - HWPX 파싱             │    │
│  │  /api/parse/excel   - Excel 파싱            │    │
│  │  /api/leave-records - 휴가 CRUD             │    │
│  │  /api/employees     - 직원 CRUD             │    │
│  │  /api/sync-excel    - DB 동기화             │    │
│  └────────────────────────────────────────────┘    │
└──────────────────┬──────────────────────────────────┘
                   │
         ┌─────────┴──────────┐
         ▼                    ▼
    ┌──────────┐        ┌──────────┐
    │ 파싱     │        │ 데이터   │
    │ 모듈     │        │ 베이스   │
    ├──────────┤        ├──────────┤
    │ HWPX →   │        │ SQLite   │
    │ JSON     │        │ 저장소   │
    │          │        │          │
    │ Excel →  │        │ 11개     │
    │ CSV      │        │ 테이블   │
    └──────────┘        └──────────┘
```

---

## 📁 파일 구조

```
grcil-erp/
├── 📄 Frontend
│   └── grcil_erp_dashboard.html      # 관리자 대시보드 UI
│
├── 🐍 Backend
│   ├── app.py                        # Flask API 서버
│   ├── hwpx_parser.py                # HWPX 파싱 엔진
│   ├── excel_parser.py               # Excel 파싱 엔진
│   └── grcil_database.py             # SQLite DB 관리
│
├── 📚 Documentation
│   ├── README.md                     # 이 파일
│   ├── QUICK_START.md                # 빠른 시작 가이드
│   └── DEPLOYMENT.md                 # 배포 가이드
│
├── 🔧 Configuration
│   ├── requirements.txt               # Python 의존성
│   ├── .gitignore                    # Git 무시 규칙
│   └── .env.example                  # 환경 변수 템플릿
│
├── 🚀 CI/CD
│   └── .github/workflows/deploy.yml   # GitHub Actions
│
└── 📦 Distribution
    └── dist/                         # 배포 파일 (자동 생성)
```

---

## 💻 기술 스택

| 계층 | 기술 | 버전 |
|------|------|------|
| **Frontend** | HTML5, CSS3, Vanilla JS | ES6+ |
| **Backend** | Python, Flask | 3.9+ / 2.0+ |
| **Database** | SQLite3 | 3.35+ |
| **Parsing** | pandas, openpyxl, zipfile, xml | 1.3+ / 3.6+ |
| **Deployment** | GitHub Pages, Netlify, Gunicorn | - |

---

## 📊 사용 예제

### HWPX 파일 파싱

```bash
# 1. API로 요청
curl -X POST http://localhost:5000/api/parse/hwpx \
  -F "file=@휴가신청서.hwpx"

# 2. 응답 예제
{
  "status": "success",
  "document_id": 1,
  "filename": "휴가신청서.hwpx",
  "parsed_data": {
    "성명": "김휘원",
    "소속": "사무행정팀",
    "직위": "간사",
    "휴가시작일": "2026-05-01",
    "휴가종료일": "2026-05-03",
    "휴가사유": "개인 사유"
  },
  "confidence": 0.95,
  "validation": {
    "valid": true,
    "errors": [],
    "warnings": []
  }
}
```

### Excel 파일 파싱

```bash
# 1. API로 요청
curl -X POST http://localhost:5000/api/parse/excel \
  -F "file=@휘원 휴가 목록.xlsx"

# 2. 응답 예제
{
  "status": "success",
  "filename": "휘원 휴가 목록.xlsx",
  "total_sheets": 3,
  "recognized_sheets": {
    "leave": {
      "sheet_name": "휴가",
      "confidence": 0.92,
      "rows": 25,
      "columns": ["직원명", "휴가시작", "휴가종료", "일수"]
    }
  }
}
```

---

## 🔐 보안 및 권한

### 개인 모드
- 🔓 로그인: 직원 이름 + 핸드폰 뒷자리
- 📊 접근: 본인 데이터만 조회 가능

### 관리자 모드
- 🔒 로그인: 관리자 비밀번호
- 🔑 권한: 전사 데이터 수정/삭제 가능
- 📋 감사: 모든 작업 로그 기록

---

## 📈 개발 로드맵

### v0.9.0 (현재 - Beta)
- ✅ HWPX/Excel 파싱 엔진
- ✅ SQLite 중앙 DB
- ✅ Flask API 서버
- ✅ GitHub 저장소

### v1.0 (예상 6월)
- 🔄 HWP/PDF 보고서 생성
- 🔄 프로덕션 배포 (Netlify)
- 🔄 사용자 매뉴얼 완성

### v1.1 (예상 7월)
- 📱 모바일 앱 (PWA)
- 🌍 다국어 지원 (영어, 중국어)
- ☁️ 자동 백업 (Google Drive)

### v2.0 (예상 9월+)
- 💾 클라우드 DB 연동 (Supabase)
- 🤖 AI 기반 자동 분류
- 📧 자동 이메일 배포
- 💬 Slack 통합

---

## 🤝 기여 가이드

### 버그 신고

1. [Issues](https://github.com/grcil/grcil-erp/issues) 탭에서 "New Issue" 클릭
2. 제목: `[버그] 파일명, 에러 메시지`
3. 설명:
   - 상황 설명 (언제/어디서 발생했는가)
   - 재현 방법
   - 스크린샷 또는 로그

### 기능 요청

1. Issues에서 "Feature Request" 템플릿 선택
2. 필요한 이유
3. 사용 사례
4. 우선순위

### Pull Request

```bash
# 1. Fork 저장소
# 2. Feature branch 생성
git checkout -b feature/기능명

# 3. 수정 및 테스트
git add .
git commit -m "feat: 기능 설명"

# 4. Push
git push origin feature/기능명

# 5. GitHub에서 Pull Request 생성
```

---

## ❓ FAQ

### Q1. 로컬에서 테스트하려면?
**A**: `python app.py` 실행 후 http://127.0.0.1:5000 접속

### Q2. 기존 Excel 파일을 자동으로 인식할 수 있나?
**A**: 네! Column 이름을 확인만 하면 자동 매핑됩니다.

### Q3. HWPX 파일이 인식 안 됩니다.
**A**: `unzip -l "파일.hwpx"`로 `document.xml` 확인하세요.

### Q4. 보고서는 언제 출력 가능한가?
**A**: v1.0에서 HWP/PDF 생성 기능 예정 (6월)

### Q5. 클라우드 백업은?
**A**: v1.1에서 Google Drive 자동 백업 예정 (7월)

---

## 📞 지원

### 문의 및 피드백

- **이메일**: grcil@daum.net
- **GitHub Issues**: https://github.com/grcil/grcil-erp/issues
- **GitHub Discussions**: https://github.com/grcil/grcil-erp/discussions

### 센터 정보

- **이름**: 구로장애인자립생활센터
- **주소**: 서울시 구로구
- **전화**: 02-1234-5678
- **웹사이트**: grcil.kr

---

## 📄 라이센스

이 프로젝트는 구로장애인자립생활센터의 내부용 시스템입니다.  
외부 배포 및 상업 이용을 금합니다.

---

## 🙏 감사

- 구로장애인자립생활센터 전 직원
- 사무행정팀 (김휘원, 노현숙, 최수연, 조승민)
- 테스트 및 피드백 참여자들

---

## 📚 추가 문서

- [빠른 시작 가이드](QUICK_START.md)
- [배포 가이드](DEPLOYMENT.md)
- [API 문서](API.md) (준비 중)
- [DB 스키마](SCHEMA.md) (준비 중)
- [사용자 매뉴얼](MANUAL.md) (준비 중)

---

**개발자**: 김휘원 (kwhiwon@grcil.kr)  
**상태**: 🔄 개발 중  
**마지막 업데이트**: 2026-05-28  
**버전**: 0.9.0 (Beta)

```
          ⚙️  구로 ERP 시스템 ⚙️
     "효율적인 인사관리, 함께하는 센터"
```
