"""
구로ERP SQLite 데이터베이스 스키마
- 직원 관리
- 휴가 관리
- 급여 관리
- 보험료 관리
- 문서 이력
- 감시 기록
"""

import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any


class GroCILDatabase:
    """구로ERP 데이터베이스 관리자"""
    
    DB_PATH = Path.home() / ".grcil_erp" / "grcil_erp.db"
    
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or self.DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
    def init_db(self):
        """데이터베이스 초기화"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 1. 조직 정보
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS organization (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                address TEXT,
                phone TEXT,
                fax TEXT,
                ceo_name TEXT,
                registration_number TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 2. 직원 정보
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                korean_name TEXT,
                position TEXT,  -- '상근직', '시간제' 등
                grade TEXT,  -- '5급', '4급' 등
                step INTEGER,  -- 호봉
                department TEXT,  -- '사무행정팀', '사업팀' 등
                join_date DATE,
                status TEXT DEFAULT 'active',  -- 'active', 'resigned', 'inactive'
                resignation_date DATE,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 3. 연봉 설정 (기본급, 수당)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS compensation_settings (
                id INTEGER PRIMARY KEY,
                employee_id INTEGER NOT NULL,
                month TEXT,  -- 'YYYY-MM'
                base_salary REAL,  -- 기본급
                meal_allowance REAL DEFAULT 0,  -- 식사비
                family_allowance REAL DEFAULT 0,  -- 가족수당
                overtime_pay REAL DEFAULT 0,  -- 초과근무비
                bonus REAL DEFAULT 0,  -- 상여금
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (employee_id) REFERENCES employees(id),
                UNIQUE(employee_id, month)
            )
        ''')
        
        # 4. 휴가 기록
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS leave_records (
                id INTEGER PRIMARY KEY,
                employee_id INTEGER NOT NULL,
                start_date DATE NOT NULL,
                end_date DATE NOT NULL,
                days REAL NOT NULL,  -- 0.5일 단위 지원
                type TEXT NOT NULL,  -- '연차', '보상', '병가', '기타'
                reason TEXT,
                status TEXT DEFAULT 'pending',  -- 'pending', 'approved', 'rejected', 'cancelled'
                approver_name TEXT,
                approval_date DATE,
                document_path TEXT,  -- 첨부된 HWP 경로
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (employee_id) REFERENCES employees(id)
            )
        ''')
        
        # 5. 연차 잔여 현황
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS annual_leave_balance (
                id INTEGER PRIMARY KEY,
                employee_id INTEGER NOT NULL,
                year INTEGER NOT NULL,
                accrued_days REAL,  -- 발생일수 (기본 15일 + 근속일수)
                used_days REAL DEFAULT 0,  -- 사용일수
                carry_over_days REAL DEFAULT 0,  -- 이월일수
                balance_days REAL,  -- 잔여일수
                notes TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (employee_id) REFERENCES employees(id),
                UNIQUE(employee_id, year)
            )
        ''')
        
        # 6. 보상휴가 관리
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS compensation_leave (
                id INTEGER PRIMARY KEY,
                employee_id INTEGER NOT NULL,
                grant_date DATE NOT NULL,
                days REAL NOT NULL,
                reason TEXT,  -- '휴일근무', '시간외근무' 등
                expiry_date DATE,  -- 만료일
                used_date DATE,
                status TEXT DEFAULT 'active',  -- 'active', 'expired', 'used'
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (employee_id) REFERENCES employees(id)
            )
        ''')
        
        # 7. 급여 명세서
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS payroll_records (
                id INTEGER PRIMARY KEY,
                employee_id INTEGER NOT NULL,
                month TEXT NOT NULL,  -- 'YYYY-MM'
                base_salary REAL,
                meal_allowance REAL,
                family_allowance REAL,
                overtime_pay REAL,
                total_income REAL,
                national_pension REAL,
                health_insurance REAL,
                employment_insurance REAL,
                income_tax REAL,
                local_tax REAL,
                total_deduction REAL,
                net_salary REAL,
                issued_date DATE,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (employee_id) REFERENCES employees(id),
                UNIQUE(employee_id, month)
            )
        ''')
        
        # 8. 보험료 현황
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS insurance_records (
                id INTEGER PRIMARY KEY,
                employee_id INTEGER NOT NULL,
                month TEXT NOT NULL,  -- 'YYYY-MM'
                national_pension_company REAL,  -- 국민연금 회사 부담
                national_pension_employee REAL,  -- 국민연금 직원 부담
                health_insurance_company REAL,  -- 건강보험 회사 부담
                health_insurance_employee REAL,  -- 건강보험 직원 부담
                employment_insurance_company REAL,  -- 고용보험 회사 부담
                employment_insurance_employee REAL,  -- 고용보험 직원 부담
                long_term_care REAL,  -- 장기요양보험
                total_company_burden REAL,  -- 회사 총 부담액
                total_employee_burden REAL,  -- 직원 총 부담액
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (employee_id) REFERENCES employees(id),
                UNIQUE(employee_id, month)
            )
        ''')
        
        # 9. 업로드된 문서
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY,
                employee_id INTEGER,
                filename TEXT NOT NULL,
                file_type TEXT,  -- 'hwpx', 'xlsx', 'pdf' 등
                file_path TEXT,
                file_size INTEGER,  -- 파일 크기 (바이트)
                parsed_data JSON,  -- 파싱된 메타데이터
                related_record_id INTEGER,  -- 관련 기록 ID
                related_record_type TEXT,  -- 'leave', 'payroll' 등
                uploaded_by TEXT,  -- 업로드 사용자
                status TEXT DEFAULT 'processed',  -- 'pending', 'processed', 'error'
                error_message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (employee_id) REFERENCES employees(id)
            )
        ''')
        
        # 10. 감시 기록 (관리자 작업 로그)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY,
                user_name TEXT,
                action TEXT,  -- 'create', 'update', 'delete', 'export', 'import'
                table_name TEXT,
                record_id INTEGER,
                old_value JSON,
                new_value JSON,
                details TEXT,
                ip_address TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 11. 시스템 설정
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_settings (
                id INTEGER PRIMARY KEY,
                setting_key TEXT UNIQUE NOT NULL,
                setting_value TEXT,
                description TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 인덱스 생성
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_employee_name ON employees(name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_leave_employee ON leave_records(employee_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_leave_dates ON leave_records(start_date, end_date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_payroll_month ON payroll_records(month)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_log(timestamp)')
        
        conn.commit()
        conn.close()
        
        print(f"✅ 데이터베이스 초기화 완료: {self.db_path}")
    
    def insert_employee(self, name: str, **kwargs) -> int:
        """직원 추가"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            columns = ['name'] + list(kwargs.keys())
            placeholders = ','.join(['?' for _ in columns])
            values = [name] + list(kwargs.values())
            
            cursor.execute(f'''
                INSERT INTO employees ({','.join(columns)})
                VALUES ({placeholders})
            ''', values)
            
            conn.commit()
            return cursor.lastrowid
            
        finally:
            conn.close()
    
    def insert_leave_record(self, employee_id: int, start_date: str, end_date: str, 
                           days: float, type_: str, **kwargs) -> int:
        """휴가 기록 추가"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            columns = ['employee_id', 'start_date', 'end_date', 'days', 'type'] + list(kwargs.keys())
            placeholders = ','.join(['?' for _ in columns])
            values = [employee_id, start_date, end_date, days, type_] + list(kwargs.values())
            
            cursor.execute(f'''
                INSERT INTO leave_records ({','.join(columns)})
                VALUES ({placeholders})
            ''', values)
            
            conn.commit()
            return cursor.lastrowid
            
        finally:
            conn.close()
    
    def get_leave_balance(self, employee_id: int, year: int) -> Dict[str, Any]:
        """연차 잔여 현황 조회"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT * FROM annual_leave_balance
                WHERE employee_id = ? AND year = ?
            ''', (employee_id, year))
            
            row = cursor.fetchone()
            return dict(row) if row else None
            
        finally:
            conn.close()
    
    def insert_document(self, employee_id: Optional[int], filename: str, 
                       file_type: str, **kwargs) -> int:
        """문서 등록"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            columns = ['employee_id', 'filename', 'file_type'] + list(kwargs.keys())
            placeholders = ','.join(['?' for _ in columns])
            values = [employee_id, filename, file_type] + list(kwargs.values())
            
            cursor.execute(f'''
                INSERT INTO documents ({','.join(columns)})
                VALUES ({placeholders})
            ''', values)
            
            conn.commit()
            return cursor.lastrowid
            
        finally:
            conn.close()
    
    def log_audit(self, user_name: str, action: str, table_name: str, 
                  record_id: int, **kwargs):
        """감시 기록 추가"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            columns = ['user_name', 'action', 'table_name', 'record_id'] + list(kwargs.keys())
            placeholders = ','.join(['?' for _ in columns])
            values = [user_name, action, table_name, record_id] + list(kwargs.values())
            
            cursor.execute(f'''
                INSERT INTO audit_log ({','.join(columns)})
                VALUES ({placeholders})
            ''', values)
            
            conn.commit()
            
        finally:
            conn.close()


# 사용 예제
if __name__ == '__main__':
    db = GroCILDatabase()
    db.init_db()
    
    # 조직 정보 추가
    conn = sqlite3.connect(db.db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT OR REPLACE INTO organization (name, address, phone, ceo_name)
        VALUES (?, ?, ?, ?)
    ''', ('구로장애인자립생활센터', '서울시 구로구', '02-1234-5678', '이사')
    )
    
    conn.commit()
    conn.close()
    
    print(f"✅ 조직 정보 추가: {db.db_path}")
