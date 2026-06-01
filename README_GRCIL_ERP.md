# 구로ERP (구로장애인자립생활센터 전자결재&HR시스템)

> **목표**: 20명 규모 사무실의 **휴가관리, 급여계산, 보고서 생성**을 한곳에서 처리
> 
> **현황**: Phase 1 (HWPX/Excel 파싱), Phase 2 (보고서 생성), Phase 3 (DB 구축) 로드맵

---

## 📋 시스템 개요

### 핵심 기능

| 기능 | 설명 | 상태 |
|------|------|------|
| **개인 대시보드** | 본인 휴가, 급여명세, 차용금 확인 | ✅ |
| **관리자 대시보드** | 전직원 HR, 급여, 보고서 생성 | 🔄 |
| **HWPX 자동 파싱** | 휴가신청서 → JSON 추출 | 🔄 |
| **Excel 자동 동기화** | 휴가현황.xlsx → DB 병합 | 🔄 |
| **HWP/PDF 보고서** | 휴가신청서, 정산보고서 생성 | ⏳ |
| **SQLite 중앙 DB** | 직원, 휴가, 급여, 문서 저장 | ⏳ |
| **감사 기록 (Audit Log)** | 관리자 모든 작업 기록 | ⏳ |

**범례**: ✅ 구현완료 | 🔄 진행중 | ⏳ 계획중

---

## 🚀 빠른 시작 (5분)

### 1단계: 환경 설정

```bash
# 필요 라이브러리 설치
pip install pandas openpyxl sqlite3

# 데이터베이스 초기화
python grcil_database.py

# 대시보드 서버 실행
python -m http.server 8091  # localhost:8091/grcil_erp_dashboard.html
```

### 2단계: 파일 업로드

1. 브라우저에서 **http://127.0.0.1:8091/grcil_erp_dashboard.html** 접속
2. **임포트** 탭 선택
3. HWPX 또는 Excel 파일 드래그앤드롭
4. 자동 파싱 결과 확인 → **저장**

### 3단계: 보고서 생성

```bash
# 급여명세서 생성
python generate_payroll_report.py --employee "김휘원" --month "2026-05"

# 휴가신청서 생성
python generate_leave_form.py --employee-id 1 --start-date "2026-05-01" --end-date "2026-05-03"
```

---

## 📁 파일 구조

```
구로ERP/
├── grcil_erp_dashboard.html      # 관리자 대시보드 (메인 UI)
├── grcil_erp_improvement_strategy.md  # 전체 로드맵
│
├── 파싱 엔진/
│   ├── hwpx_parser.py            # HWPX 자동 분석
│   └── excel_parser.py           # Excel Sheet 자동 인식
│
├── 데이터베이스/
│   └── grcil_database.py         # SQLite 스키마 & CRUD
│
├── 보고서 생성/
│   ├── generate_payroll_report.py     # 급여명세서
│   ├── generate_leave_form.py         # 휴가신청서
│   └── generate_settlement_report.py  # 정산보고서
│
├── 백엔드 API/
│   ├── app.py                    # Flask 또는 FastAPI
│   └── config.py                 # 설정 파일
│
└── 테스트 파일/
    ├── sample_leave_form.hwpx
    ├── 휘원 휴가 목록.xlsx
    └── test_data.py
```

---

## 🔧 주요 기술 스택

### Frontend
- **HTML5 / CSS3**: 반응형 대시보드
- **Vanilla JS**: 드래그앤드롭, 탭 전환, 상태 관리
- **localStorage**: 임시 데이터 저장

### Backend
- **Python 3.9+**
  - `pandas`: Excel/CSV 파싱
  - `openpyxl`: Excel 생성
  - `zipfile`: HWPX (ZIP) 해제
  - `xml.etree`: XML 파싱
  - `sqlite3`: 로컬 DB
  - `python-docx`: 문서 생성 (향후)

### 데이터베이스
- **SQLite3**: 로컬 저장 (`.db` 파일)
  - 테이블: employees, leave_records, payroll_records, documents, audit_log 등

---

## 📊 데이터 흐름

```
┌─────────────────────┐
│  HWPX / Excel 파일  │
└──────────┬──────────┘
           │
           ▼
┌──────────────────────────────────┐
│  자동 파싱 엔진                   │
│  - HWPX → document.xml → JSON   │
│  - Excel → pandas DataFrame     │
└──────────┬───────────────────────┘
           │
           ▼
┌──────────────────────────────────┐
│  데이터 검증 & 병합               │
│  - 중복 제거 (Upsert)            │
│  - 형식 검증                     │
│  - Audit Log 기록                │
└──────────┬───────────────────────┘
           │
           ▼
┌──────────────────────────────────┐
│  SQLite 중앙 DB                  │
│  - employees 테이블              │
│  - leave_records 테이블          │
│  - payroll_records 테이블        │
└──────────┬───────────────────────┘
           │
           ▼
┌──────────────────────────────────┐
│  보고서 생성 (HWP/PDF)            │
│  - 휴가신청서 (개인)              │
│  - 정산보고서 (월별)              │
│  - 급여명세서 (개인)              │
└──────────────────────────────────┘
```

---

## 💻 사용 예제

### HWPX 파일 파싱

```python
from hwpx_parser import HWPXParser, HWPXValidator

# 파일 파싱
parser = HWPXParser('휴가신청서.hwpx')
result = parser.parse()

print(result['from_text'])  # {'성명': '김휘원', '소속': '사무행정팀', ...}

# 검증
validator = HWPXValidator()
validation = validator.validate_leave_form(result)
print(validation['valid'])  # True or False
```

### Excel 파일 자동 인식

```python
from excel_parser import ExcelParser, ExcelMerger

# 파일 분석
parser = ExcelParser('휴가현황.xlsx')
result = parser.parse()

print(result.recognized_sheets)  
# {'leave': {'sheet_name': '휴가', 'confidence': 0.92, 'rows': 25, ...}}

# 기존 DB와 병합
merger = ExcelMerger()
merge_result = merger.merge_leave_records(
    existing_data,
    new_dataframe,
    column_mapping
)
print(merge_result['summary'])  # {'inserted': 3, 'updated': 5}
```

### SQLite 데이터 저장

```python
from grcil_database import GroCILDatabase

db = GroCILDatabase()
db.init_db()

# 직원 추가
emp_id = db.insert_employee(
    name='김휘원',
    position='간사',
    grade='5급',
    step=7,
    join_date='2016-01-15'
)

# 휴가 기록 추가
leave_id = db.insert_leave_record(
    employee_id=emp_id,
    start_date='2026-05-01',
    end_date='2026-05-03',
    days=3,
    type_='연차',
    reason='개인 사유'
)

# 감시 기록
db.log_audit(
    user_name='관리자',
    action='create',
    table_name='leave_records',
    record_id=leave_id
)
```

---

## 📅 일일 / 월별 운영 프로세스

### 월초 (1-5일)
- [ ] 직원정보 확인 (입사/퇴사 없음 확인)
- [ ] 급여 기본정보 입력 (기본급, 수당)
- [ ] 이전 달 연차 사용 현황 정리

### 월중 (5-25일)
- [ ] 휴가신청서 HWPX 파일 시스템 업로드
  ```bash
  python grcil_erp_dashboard.html → 임포트 탭 → HWPX 드래그앤드롭
  ```
- [ ] 승인된 휴가 수량 확인
- [ ] 보상휴가 기록 (휴일근무 있을 시)

### 월말 (25-말일)
- [ ] 급여 계산
  ```bash
  python generate_payroll_report.py --month "2026-05"
  ```
- [ ] 4대보험료 계산 및 확인
- [ ] 급여명세서 생성 & 배포
- [ ] 정산보고서 생성
  ```bash
  python generate_settlement_report.py --month "2026-05"
  ```

### 연말 (12월)
- [ ] 연차 이월 계산
- [ ] 정산 및 보상휴가 정리
- [ ] 세무 양식 생성 (연말정산)

---

## 🔐 권한 관리

### 개인 모드
- ✅ 본인 휴가 내역 조회
- ✅ 본인 급여명세 조회
- ❌ 다른 직원 정보 조회 불가
- ❌ 데이터 수정/삭제 불가

### 관리자 모드
- ✅ 모든 직원 정보 조회
- ✅ 휴가 승인/반려
- ✅ 급여 계산 및 수정
- ✅ 보고서 생성
- ✅ 문서 업로드
- ✅ 감시 기록 조회

**접근**: 관리자 비밀번호 입력 시 전환

---

## ❓ FAQ

### Q1. HWPX 파일이 인식되지 않습니다.
**A**: 다음을 확인하세요:
1. 파일이 실제 HWPX 형식인가? (ZIP으로 압축 해제 가능한가)
2. `document.xml` 또는 `content.xml`이 포함되어 있는가?
3. 파일 인코딩이 UTF-8인가?

```bash
unzip -l "파일명.hwpx"  # 내용 확인
```

### Q2. Excel 업로드 후 데이터가 안 보입니다.
**A**: Column 이름을 확인하세요:
- ✅ 지원: "직원", "성명", "이름" (대소문자 무관)
- ❌ 지원 안 함: "A", "Column1"

Column 이름을 표준 형식으로 수정 후 재업로드:
```
휴가 → 직원명, 시작일, 종료일, 일수, 유형, 사유
직원 → 성명, 직위, 부서, 입사일
급여 → 직원명, 기본급, 수당
```

### Q3. 보고서 PDF 글씨가 깨집니다.
**A**: 한글 폰트 설치 확인:
```bash
# Linux
sudo apt-get install fonts-noto-cjk

# macOS
brew install font-noto-sans-cjk

# Windows
# "나눔고딕" 또는 "맑은 고딕" 폰트 설치
```

### Q4. 어제 업로드한 파일을 찾을 수 없습니다.
**A**: 변환 이력 탭을 확인하세요:
```
임포트 탭 → 변환 이력 → 파일명으로 검색
```

히스토리에 없으면 다시 업로드하세요. (로컬 저장: `~/.grcil_erp/documents/`)

### Q5. 여러 파일을 한 번에 업로드할 수 있나요?
**A**: 현재는 1개씩만 지원합니다. 대량 업로드는 다음에서 구현 예정:
```python
# 향후 기능
batch_upload_files(['file1.hwpx', 'file2.xlsx', ...])
```

---

## 🐛 알려진 문제 (Known Issues)

| 문제 | 상태 | 예상 해결 |
|------|------|---------|
| HWPX 중첩 테이블 미지원 | 🔴 | v1.2 |
| Excel 병합 셀 미지원 | 🔴 | v1.2 |
| 다국어 PDF 렌더링 | 🟡 | v1.1 |
| 대량 파일 처리 (>100MB) | 🟡 | v2.0 |
| 자동 이메일 배포 | ⚪ | v2.0 |

**범례**: 🔴 높음 | 🟡 중간 | ⚪ 낮음

---

## 📞 지원 및 피드백

### 버그 신고
```
메일: grcil@daum.net
제목: [ERP 버그] 파일명, 에러 메시지
내용: 
  - 상황 설명
  - 파일 첨부 (선택)
  - 스크린샷 (선택)
```

### 기능 요청
```
메일: grcil@daum.net
제목: [ERP 기능 요청] 기능명
내용:
  - 필요한 이유
  - 사용 사례
  - 우선순위
```

---

## 📚 추가 문서

- [전체 기술 로드맵](grcil_erp_improvement_strategy.md)
- [API 문서](api_documentation.md) ⏳
- [DB 스키마](database_schema.md) ⏳
- [사용자 매뉴얼](user_manual.md) ⏳

---

## 🎯 향후 계획 (Roadmap)

### v1.0 (2026-06월)
- ✅ HWPX/Excel 자동 파싱
- ✅ SQLite 중앙 DB
- 🔄 HWP/PDF 보고서 생성

### v1.1 (2026-07월)
- 🔄 다국어 지원 (영어, 중국어)
- 🔄 모바일 앱 베타 (PWA)
- 🔄 자동 백업 (Google Drive)

### v1.2 (2026-08월)
- 대량 파일 처리 최적화
- 예외 케이스 처리 (중첩 테이블, 병합 셀)
- 성능 모니터링 대시보드

### v2.0 (2026-09월 이후)
- ☁️ 클라우드 동기화 (Supabase)
- 📱 Native Mobile App
- 🤖 AI 기반 자동 분류 (급여, 휴가 유형)
- 📧 이메일 자동 배포
- 💬 Slack 통합

---

## 📄 라이센스

**내부용 시스템** - 구로장애인자립생활센터 전용

---

## 👨‍💼 개발자

- **김휘원** (kwhiwon@grcil.kr)
  - 기획, 백엔드 (Python)
  - DB 설계, 자동화 스크립트

---

## 🙏 감사

- 구로장애인자립생활센터 전 직원
- 테스트 및 피드백 참여자들

---

**Last Updated**: 2026-05-28  
**Version**: 0.9.0 (Beta)  
**Status**: 🔄 Active Development

```
          ⚙️  구로 ERP 시스템 ⚙️
     "효율적인 인사관리, 함께하는 센터"
```
