# 구로ERP 프로젝트 - 즉시 실행 가이드

## 📌 개요

**목표**: 구로장애인자립생활센터의 현재 웹 기반 휴가관리 시스템을 **ERP 수준으로 고도화**

**현재 상태**:
- ✅ 개인/관리자 모드 분리 완료 (localhost:8091)
- ✅ 개인 휴가 달력 & 보상휴가 로직 완료
- ❌ HWPX 자동 인식 미흡
- ❌ 엑셀 자동 업로드/분석 기능 부재
- ❌ 중앙 데이터베이스 없음

---

## 📦 생성된 파일 목록 (6개)

### 1️⃣ **전략 문서**

#### `grcil_erp_improvement_strategy.md` (9.4 KB)
- **내용**: 전체 기술 로드맵, Phase별 계획
- **대상**: 기획자, PM
- **핵심**:
  - Phase 1: HWPX/Excel 파싱 (1주)
  - Phase 2: HWP/PDF 보고서 생성 (1-2주)
  - Phase 3: SQLite 중앙 DB (1주)
  - Phase 4: ERP 메뉴 통합 (2주)

---

### 2️⃣ **백엔드 모듈** (Python)

#### `hwpx_parser.py` (8.3 KB)
**기능**: HWPX 파일 자동 파싱 → JSON 추출
```python
from hwpx_parser import HWPXParser

parser = HWPXParser('휴가신청서.hwpx')
result = parser.parse()
# {'성명': '김휘원', '소속': '사무행정팀', '휴가기간': '2026-05-01~05-03', ...}
```

**지원 필드**:
- 기본 정보: 소속, 직위, 성명
- 휴가 정보: 휴가시작일, 휴가종료일, 휴가사유
- 승인: 업무이관, 결재자
- 신뢰도: 자동 계산 (%)

**기술**:
- ZIP 파일 해제
- XML 파싱
- 정규식 기반 필드 추출

---

#### `excel_parser.py` (11 KB)
**기능**: Excel Sheet 자동 인식 → 데이터 검증 및 병합

```python
from excel_parser import ExcelParser, ExcelMerger

parser = ExcelParser('휴가현황.xlsx')
result = parser.parse()

print(result.recognized_sheets)
# {'leave': {'sheet_name': '휴가', 'confidence': 0.92, 'rows': 25, ...}}

# 기존 DB와 병합 (Upsert)
merge_result = ExcelMerger.merge_leave_records(
    existing_data, new_df, column_mapping
)
# {'inserted': 3, 'updated': 5}
```

**인식 기능**:
- Sheet 유형 자동 감지 (휴가, 직원, 급여, 보상)
- Column 자동 매핑 (방언 처리)
  - "직원", "성명", "이름" → 표준화
- 데이터 검증
  - 필수 필드 확인
  - 날짜 형식 검증
  - 중복 감지

---

#### `grcil_database.py` (14 KB)
**기능**: SQLite 스키마 생성 및 CRUD 작업

```python
from grcil_database import GroCILDatabase

db = GroCILDatabase()
db.init_db()  # 자동 스키마 생성

# 직원 추가
emp_id = db.insert_employee(
    name='김휘원', position='간사', grade='5급', step=7
)

# 휴가 기록
leave_id = db.insert_leave_record(
    employee_id=emp_id,
    start_date='2026-05-01',
    end_date='2026-05-03',
    days=3,
    type_='연차'
)

# 감시 로그
db.log_audit('관리자', 'create', 'leave_records', leave_id)
```

**11개 테이블**:
- `employees`: 직원 정보
- `leave_records`: 휴가 기록
- `compensation_leave`: 보상휴가
- `payroll_records`: 급여 명세
- `insurance_records`: 보험료
- `documents`: 업로드된 파일
- `audit_log`: 감시 기록
- 기타 5개

**저장소**: `~/.grcil_erp/grcil_erp.db` (로컬)

---

### 3️⃣ **프론트엔드**

#### `grcil_erp_dashboard.html` (28 KB)
**기능**: 관리자 대시보드 + HWPX/Excel 업로드 UI

**화면 구성**:
1. **사이드바 메뉴**
   - 📊 대시보드
   - 📤 임포트 (HWPX, Excel)
   - 👥 직원 관리
   - 📅 휴가 관리
   - 💰 급여 관리
   - 📄 보고서
   - ⚙️ 설정

2. **임포트 탭** (핵심)
   - HWPX 드래그앤드롭 → 자동 파싱
   - Excel 드래그앤드롭 → Sheet 인식
   - 변환 이력 조회

3. **디자인**
   - 구로센터 색상 (청록색 #1e7e74)
   - 프로페셔널 한글 폰트
   - 반응형 (데스크톱)
   - 다크 모드 고려

**특징**:
- 드래그앤드롭 지원
- 로딩 스피너
- 신뢰도 배지
- 결과 테이블
- 즉시 저장 버튼

---

### 4️⃣ **문서**

#### `README_GRCIL_ERP.md` (12 KB)
**내용**: 운영 가이드, 사용 예제, FAQ, 로드맵

**섹션**:
- 빠른 시작 (5분)
- 파일 구조
- 기술 스택
- 데이터 흐름도
- 일일/월별 프로세스
- 권한 관리
- FAQ & 알려진 문제
- 향후 계획 (v1.1 ~ v2.0)

---

## 🎯 즉시 실행 단계

### Step 1: 파일 다운로드 ⏱️ 2분

```bash
cd ~/프로젝트폴더/구로ERP

# 모든 파일 다운로드
# - grcil_erp_improvement_strategy.md
# - hwpx_parser.py
# - excel_parser.py
# - grcil_database.py
# - grcil_erp_dashboard.html
# - README_GRCIL_ERP.md
```

### Step 2: 환경 설정 ⏱️ 5분

```bash
# Python 라이브러리 설치
pip install pandas openpyxl

# 데이터베이스 초기화
python grcil_database.py

# 출력:
# ✅ 데이터베이스 초기화 완료: /home/user/.grcil_erp/grcil_erp.db
# ✅ 조직 정보 추가: /home/user/.grcil_erp/grcil_erp.db
```

### Step 3: 대시보드 실행 ⏱️ 1분

```bash
# 현재 폴더에서 로컬 서버 실행
python -m http.server 8091

# 또는 (Python 2.x)
python -m SimpleHTTPServer 8091

# 브라우저에서 접속
# http://127.0.0.1:8091/grcil_erp_dashboard.html
```

### Step 4: 파일 업로드 테스트 ⏱️ 5분

**테스트 시나리오 A**: HWPX 파일
1. 기존 `휴가신청서.hwpx` 파일 준비 (또는 새로 생성)
2. 대시보드 → 임포트 탭 → HWPX 탭
3. 파일 드래그앤드롭
4. **기대 결과**: 자동으로 필드 추출 (성명, 소속, 휴가기간 등)

**테스트 시나리오 B**: Excel 파일
1. `휘원 휴가 목록.xlsx` 파일 준비
2. 대시보드 → 임포트 탭 → Excel 탭
3. 파일 드래그앤드롭
4. **기대 결과**: Sheet 자동 인식 (휴가, 직원, 급여 등)

---

## 🔧 각 모듈 테스트 방법

### HWPX 파서 테스트

```bash
# 1. hwpx_parser.py 하단의 테스트 코드 실행
python hwpx_parser.py

# 2. 샘플 파일로 테스트
python -c "
from hwpx_parser import HWPXParser
parser = HWPXParser('sample_leave_form.hwpx')
result = parser.parse()
import json
print(json.dumps(result, ensure_ascii=False, indent=2))
"
```

### Excel 파서 테스트

```bash
# 1. excel_parser.py 하단의 테스트 코드 실행
python excel_parser.py

# 2. 실제 파일 테스트
python -c "
from excel_parser import ExcelParser
parser = ExcelParser('휘원 휴가 목록.xlsx')
result = parser.parse()
print(f'Sheet 수: {result.total_sheets}')
print(f'인식된 Sheet: {list(result.recognized_sheets.keys())}')
print(f'신뢰도: {result.confidence:.1%}')
"
```

### 데이터베이스 테스트

```bash
# 1. DB 초기화 및 샘플 데이터 추가
python grcil_database.py

# 2. DB 내용 확인
python -c "
import sqlite3
from pathlib import Path

db_path = Path.home() / '.grcil_erp' / 'grcil_erp.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 테이블 목록
cursor.execute(\"SELECT name FROM sqlite_master WHERE type='table'\")
tables = cursor.fetchall()
print('테이블:', [t[0] for t in tables])

conn.close()
"
```

---

## 📊 통합 워크플로우

```
기존 시스템 (localhost:8091)
├─ 개인 모드: 자신의 휴가, 급여 조회
└─ 관리자 모드: 전사 HR 관리

↓ 개선 추가

새로운 대시보드 (grcil_erp_dashboard.html)
├─ HWPX 자동 파싱 → hwpx_parser.py
├─ Excel 자동 동기화 → excel_parser.py
└─ 중앙 DB 저장 → grcil_database.py → SQLite

↓ Phase 2에서

보고서 생성
├─ 휴가신청서.hwp (개인)
├─ 정산보고서.pdf (월/분기)
└─ 급여명세서.pdf (개인)
```

---

## ⚠️ 주의사항

### 1. HWPX 파일 준비
- **필수**: `document.xml` 또는 `content.xml` 포함
- **확인**: `unzip -l "파일.hwpx"` 로 확인 가능

### 2. Excel 파일 형식
- **권장 Column 이름**: "직원명", "휴가시작일", "휴가종료일" 등
- **방언 처리**: 파서가 자동으로 매핑 ("성명", "이름" ↔ "직원명")

### 3. 한글 인코딩
- **Python**: UTF-8 인코딩 기본값
- **Excel**: ANSI (CP-949)도 지원

### 4. 보안
- **관리자 비밀번호**: 기존 시스템의 비밀번호 유지
- **DB 위치**: `~/.grcil_erp/` (숨김 폴더)

---

## 🚨 트러블슈팅

### 문제 1: "ModuleNotFoundError: No module named 'pandas'"
```bash
# 해결
pip install pandas openpyxl
```

### 문제 2: "BadZipFile" 에러 (HWPX)
```bash
# 원인: 파일이 실제 ZIP이 아님
# 확인
file "파일명.hwpx"

# 해결: 정확한 HWPX 파일 사용
```

### 문제 3: "localhost:8091 연결 불가"
```bash
# 1. 포트 사용 확인
lsof -i :8091

# 2. 다른 포트로 시도
python -m http.server 8090

# 3. 브라우저에서 http://127.0.0.1:8090/... 접속
```

### 문제 4: "엑셀 Sheet가 인식되지 않음"
```bash
# 확인: Sheet 이름이 한글인가?
# Column 이름이 정규화되어 있는가?

# 디버그
python excel_parser.py  # 테스트 코드 실행
```

---

## 📈 다음 단계 (Phase별)

### Phase 1 (지금): HWPX/Excel 파싱 ✅ 진행중
- [x] HWPX 파서 모듈 작성
- [x] Excel 파서 모듈 작성
- [x] SQLite 스키마 설계
- [x] Frontend 대시보드 UI
- [ ] 백엔드 API 통합 (Flask/FastAPI)
- [ ] 실제 파일로 테스트

### Phase 2 (1-2주 후): 보고서 생성
- [ ] `generate_payroll_report.py` 작성
- [ ] `generate_leave_form.py` 작성
- [ ] HWP 템플릿 준비
- [ ] PDF 변환 (LibreOffice)

### Phase 3 (2-3주 후): DB 통합
- [ ] 로컬 파일 → SQLite 마이그레이션
- [ ] 자동 백업 스크립트
- [ ] 데이터 동기화 (USB/클라우드)

### Phase 4 (3-4주 후): ERP 완성
- [ ] 메뉴 통합
- [ ] 권한 제어 (RBAC)
- [ ] 감사 로그 조회
- [ ] GitHub Pages README

---

## 📞 질문 및 지원

**문제 발생 시**:
1. 이 README의 FAQ & 트러블슈팅 섹션 참고
2. 파이썬 테스트 코드 실행해서 구체적 에러 확인
3. 에러 메시지 + 파일 샘플 준비
4. grcil@daum.net 으로 연락

---

## 📋 체크리스트

- [ ] 6개 파일 모두 다운로드
- [ ] Python 라이브러리 설치 (`pip install pandas openpyxl`)
- [ ] 데이터베이스 초기화 (`python grcil_database.py`)
- [ ] 로컬 서버 실행 (`python -m http.server 8091`)
- [ ] 대시보드 접속 (`http://127.0.0.1:8091/grcil_erp_dashboard.html`)
- [ ] HWPX 파일 업로드 테스트
- [ ] Excel 파일 업로드 테스트
- [ ] DB에서 데이터 확인
- [ ] README 정독

---

**작성일**: 2026-05-28  
**버전**: 0.9.0 (Beta)  
**예상 완성**: 2026-06-30

---

## 💡 핵심 기억사항

```
구로ERP = 3가지 기술

1️⃣ HWPX/Excel 자동 파싱
   → hwpx_parser.py + excel_parser.py
   
2️⃣ 중앙 데이터베이스 (SQLite)
   → grcil_database.py
   
3️⃣ 웹 기반 대시보드
   → grcil_erp_dashboard.html

이 3가지가 연결되면 완성! 🎉
```
