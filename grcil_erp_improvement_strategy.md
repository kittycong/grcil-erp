# 구로장애인자립생활센터 ERP 시스템 고도화 전략

## 📋 현재 상태 분석

### 기존 시스템 강점
- ✅ 개인/관리자 모드 분리 완료
- ✅ 개인 휴가 관리 (달력, 사용 내역)
- ✅ 보상휴가(대체휴가) 로직 구현
- ✅ 관리자 비밀번호 보안
- ✅ 개인링크 복사 기능
- ✅ 로컬 데이터 저장소 (localStorage)

### 현재 제한사항
- ❌ HWPX 양식 자동 인식 미흡
- ❌ 엑셀 자동 업로드/분석 기능 부재
- ❌ 보고서 생성/다운로드 기능 미흡
- ❌ 중앙 데이터베이스 없음 (로컬 저장만)
- ❌ ERP 통합 메뉴 구조 미완성

---

## 🎯 Phase 1: 데이터 처리 고도화 (즉시 실행)

### 1.1 HWPX 자동 인식 및 연동
**목표**: 휘원이 작성한 HWP 양식 자동 파싱 및 필드 추출

#### 구현 방식
```
Frontend (HTML/JS)
  ├─ File Input (HWPX 드래그앤드롭)
  └─ FormData 전송
       ↓
Backend (Worker/API)
  ├─ HWPX → ZIP 압축 해제
  ├─ document.xml 추출
  ├─ XML 파싱 → JSON 필드 매핑
  └─ 기존 시스템 데이터와 병합
       ↓
Database
  └─ 직원별 휴가신청 문서 이력 저장
```

**필드 매핑 예시** (HWP 연차신청서 표준양식)
```json
{
  "소속": "string",
  "직위": "string",
  "성명": "string",
  "휴가시작일": "date",
  "휴가종료일": "date",
  "휴가일수": "number",
  "사유": "string",
  "업무이관": "string",
  "결재자": "string",
  "결재일": "date"
}
```

### 1.2 엑셀 자동 업로드 및 인식
**목표**: "휘원 휴가 목록.xlsx" 같은 임시 파일 → 시스템 자동 동기화

#### 구현 구조
```
File Upload (Excel)
  ├─ Sheet 자동 인식 (휴가, 직원, 급여 등)
  └─ Column Header 매핑
       ↓
Data Validation
  ├─ 날짜 형식 검증 (YYYY-MM-DD)
  ├─ 직원 존재 여부 확인
  └─ 중복 데이터 감지
       ↓
Database Update
  ├─ 신규 데이터 삽입
  ├─ 기존 데이터 병합 (Upsert)
  └─ 충돌 로그 기록
       ↓
Report Generation
  └─ 업로드 결과 요약 (추가/수정/오류)
```

**인식 가능 Sheet 패턴**
| Sheet 이름 | 주요 Column | 기능 |
|-----------|-----------|------|
| 휴가 | 직원명, 휴가기간, 일수, 유형 | 휴가 데이터 동기화 |
| 직원 | 성명, 직위, 소속, 입사일 | 직원정보 업데이트 |
| 급여 | 직원명, 기본급, 수당 | 급여 정보 병합 |
| 보상 | 직원명, 날짜, 일수 | 대체휴가 반영 |

---

## 🎯 Phase 2: 보고서 생성 및 출력 (1-2주)

### 2.1 HWP 동적 생성 (정산보고서, 휴가신청서)
**목표**: 시스템 데이터 → HWP 양식 자동 작성 후 다운로드

#### 구현 기술 스택
```
Frontend
  └─ "보고서 생성" 버튼 클릭
       ↓
Backend API
  ├─ 직원 데이터 조회
  ├─ 휴가/급여 계산
  └─ HWP Template에 데이터 바인딩
       ↓
HWP Generation Engine
  ├─ python-pptx 등 (테이블, 텍스트)
  ├─ 또는 LibreOffice UNO Bridge
  └─ 또는 낮은 수준: ZIP + XML 직접 조작
       ↓
File Output
  └─ 다운로드 링크 제공 (.hwp)
```

**생성 가능 보고서**
1. **휴가신청서** (개인)
   - 입력값: 직원명, 휴가 기간, 사유
   - 출력: HWP + PDF

2. **정산보고서** (부서/전사)
   - 입력값: 기간, 부서
   - 출력: 급여 정산표, 휴가 사용현황, 보험료 등

3. **월별 급여명세서** (개인)
   - 입력값: 직원, 월
   - 출력: HWP 또는 PDF (나눔셈 스타일)

### 2.2 PDF 자동 생성
**목표**: 보고서를 즉시 프린트 가능한 PDF로 변환

```
HWP 생성
  └─ LibreOffice Headless Convert
       ↓
PDF Output (with Korean Font)
  └─ 다운로드 제공
```

---

## 🎯 Phase 3: 중앙 데이터 저장소 (2-3주)

### 3.1 로컬 vs. 클라우드 선택

#### 옵션 A: 로컬 SQLite (추천 - 즉시 구현)
**장점**: 인터넷 불필요, 설치 간단, 모든 데이터 로컬 유지
**단점**: 데스크톱 전용, 백업 수동 필요

```
구조:
  ├─ grcil_erp.db (SQLite)
  │  ├─ employees (직원)
  │  ├─ leave_records (휴가)
  │  ├─ payroll (급여)
  │  ├─ documents (업로드된 파일)
  │  └─ audit_log (감사 기록)
  └─ backend.py (Flask/FastAPI)
```

#### 옵션 B: Supabase (향후 - 멀티유저 필요시)
**장점**: 클라우드 동기화, 멀티디바이스, 자동 백업
**단점**: 인터넷 필수, 초기 설정 복잡

### 3.2 Schema 설계

```sql
-- 직원
CREATE TABLE employees (
  id INTEGER PRIMARY KEY,
  name TEXT,
  grade TEXT,
  step INTEGER,
  position TEXT,
  department TEXT,
  join_date DATE,
  created_at TIMESTAMP
);

-- 휴가 기록
CREATE TABLE leave_records (
  id INTEGER PRIMARY KEY,
  employee_id INTEGER,
  start_date DATE,
  end_date DATE,
  days NUMBER,
  type TEXT, -- '연차', '보상', '병가' 등
  reason TEXT,
  document_path TEXT, -- 첨부 HWP 경로
  approval_status TEXT,
  created_at TIMESTAMP,
  FOREIGN KEY (employee_id) REFERENCES employees(id)
);

-- 업로드된 문서
CREATE TABLE documents (
  id INTEGER PRIMARY KEY,
  employee_id INTEGER,
  filename TEXT,
  file_type TEXT, -- 'hwpx', 'xlsx'
  content BLOB,
  parsed_data JSON,
  uploaded_at TIMESTAMP,
  FOREIGN KEY (employee_id) REFERENCES employees(id)
);

-- 감시 기록 (관리자용)
CREATE TABLE audit_log (
  id INTEGER PRIMARY KEY,
  action TEXT,
  user_role TEXT,
  details JSON,
  timestamp TIMESTAMP
);
```

---

## 🎯 Phase 4: ERP 통합 메뉴 구조

### 4.1 사이드바 메뉴 (관리자 모드)

```
📊 대시보드
  ├─ 주요 통계 (휴가 사용률, 급여, 보험)
  └─ 최근 활동 로그

👥 인사관리
  ├─ 직원 목록
  ├─ 직원 정보 편집
  ├─ 신규 직원 등록
  └─ 직원 퇴직 처리

📅 휴가관리
  ├─ 전체 휴가 현황
  ├─ 개인별 휴가 상세
  ├─ 휴가 신청 승인/반려
  ├─ 보상휴가 관리
  └─ 휴가 내역 엑셀 다운로드

💰 급여관리
  ├─ 급여 등급표 (hobong)
  ├─ 월별 급여 계산
  ├─ 급여명세서 생성/출력
  ├─ 보험료 계산 (4대보험)
  ├─ 세금 계산 (간이세액표)
  └─ 급여 이력 조회

📄 보고서
  ├─ 휴가신청서 (HWP 생성)
  ├─ 정산보고서 (월/분기/연)
  ├─ 급여 현황표
  ├─ 보험료 납입 현황
  └─ 감사 기록

⚙️ 설정
  ├─ 조직 정보 (센터 이름, 주소)
  ├─ 급여 설정 (기본급, 수당)
  ├─ 휴가 설정 (연차 발생일, 기본일수)
  ├─ 보험료 설정
  ├─ 관리자 비밀번호 변경
  └─ 데이터 백업/복원

📤 임포트/익스포트
  ├─ HWPX 업로드 → 자동 파싱
  ├─ 엑셀 업로드 → 자동 동기화
  ├─ 데이터 엑셀 내보내기
  ├─ 보고서 PDF 내보내기
  └─ 데이터 백업 (ZIP)

🔐 접근 제어
  ├─ 직원별 접근 권한 설정
  ├─ 역할 기반 권한 (관리자/감시/제한)
  └─ 감시 기록 조회
```

---

## 💻 기술 스택 제안

### Frontend
- **현재**: HTML/CSS/JS + localStorage
- **개선**: 
  - React (상태 관리 고도화)
  - Tailwind CSS (일관된 스타일링)
  - shadcn/ui (프로페셔널 컴포넌트)

### Backend
- **언어**: Python (Flask 또는 FastAPI)
- **라이브러리**:
  - `openpyxl`: 엑셀 파싱/생성
  - `python-docx`: DOCX 생성 (HWP 전 단계)
  - `zipfile`: HWPX 파싱 (HWP 대체)
  - `reportlab`: PDF 생성
  - `sqlite3`: 로컬 DB

### 데이터 저장
- **로컬**: SQLite (즉시)
- **동기화**: Git + 주기적 백업

---

## 📆 구현 타임라인

| Phase | 목표 | 예상 기간 | 우선순위 |
|-------|------|---------|---------|
| 1 | HWPX/XLSX 자동 업로드 & 파싱 | 1주 | 🔴 높음 |
| 2 | HWP/PDF 보고서 생성 | 1-2주 | 🔴 높음 |
| 3 | SQLite DB 구축 | 1주 | 🟡 중간 |
| 4 | ERP 메뉴 통합 | 2주 | 🟡 중간 |
| 5 | 다중 사용자 동기화 | 2주 | 🟢 낮음 |

---

## 🚀 즉시 실행 가능한 작업 (오늘)

1. **HWPX 파싱 모듈** 작성
   - Input: .hwpx 파일
   - Output: JSON 필드 맵

2. **엑셀 업로드 폼** 추가
   - 드래그앤드롭 UI
   - Sheet 자동 인식
   - 데이터 검증 로직

3. **SQLite 스키마** 정의
   - 테이블 생성 스크립트
   - 초기 데이터 마이그레이션

4. **HWP 템플릿** 준비
   - 기존 "휴가신청서" 파일
   - "급여명세서" 템플릿
   - "정산보고서" 템플릿

---

## 📝 문서화 및 README

### GitHub Pages README (20명 사무실 운영 방식)
```markdown
# 구로ERP 운영 매뉴얼

## 시스템 구성
- 개인 모드: 자신의 휴가, 급여명세서만 조회
- 관리자 모드: 전사 HR, 급여, 보고서 생성

## 일일 업무 프로세스
1. 월초: 직원정보 & 급여정보 확인
2. 월중: 휴가신청서 검수 (HWP 생성)
3. 월말: 급여 계산 & 정산보고서 생성
4. 분기말: 보험료 납입 현황 확인

## FAQ
- [Q] HWPX 파일이 인식안됨?
- [Q] 엑셀 업로드 후 데이터가 안보임?
- [Q] 보고서 PDF 글씨가 깨짐?
```

---

## ✅ 체크리스트

- [ ] HWPX 파싱 엔진 구현
- [ ] Excel 업로드 프론트엔드 UI
- [ ] SQLite DB 스키마 작성
- [ ] 보고서 생성 API
- [ ] HWP/PDF 생성 모듈
- [ ] 관리자 대시보드 통합
- [ ] 권한 제어 (RBAC) 구현
- [ ] 감시 로그 추가
- [ ] 사용자 매뉴얼 작성
- [ ] 데이터 백업 스크립트
