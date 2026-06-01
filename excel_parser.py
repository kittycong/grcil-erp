"""
Excel 자동 업로드 & 파싱 엔진
- Sheet 자동 인식 (휴가, 직원, 급여)
- Column Header 매핑
- 데이터 검증 및 병합
- JSON 결과 반환
"""

import pandas as pd
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import json
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime


class SheetType(Enum):
    """인식 가능한 Sheet 유형"""
    LEAVE = "leave"          # 휴가
    EMPLOYEE = "employee"    # 직원정보
    PAYROLL = "payroll"      # 급여
    COMPENSATION = "compensation"  # 보상휴가
    UNKNOWN = "unknown"


@dataclass
class ParseResult:
    """파싱 결과"""
    filename: str
    parse_date: str
    total_sheets: int
    recognized_sheets: Dict[SheetType, Dict[str, Any]]
    errors: List[str]
    warnings: List[str]
    confidence: float


class ExcelDetector:
    """Sheet 유형 자동 인식"""
    
    SHEET_KEYWORDS = {
        SheetType.LEAVE: ['휴가', '연차', 'leave', 'vacation', '휴직'],
        SheetType.EMPLOYEE: ['직원', 'employee', 'staff', '사원', '인사'],
        SheetType.PAYROLL: ['급여', 'payroll', 'salary', '봉급', '급료'],
        SheetType.COMPENSATION: ['보상', '대체', 'compensation', '보상휴가'],
    }
    
    COLUMN_PATTERNS = {
        SheetType.LEAVE: {
            'employee_name': ['직원', '성명', '이름', '직원명', 'name'],
            'start_date': ['시작', '시작일', '휴가시작', 'start', '기간'],
            'end_date': ['종료', '종료일', '휴가종료', 'end'],
            'days': ['일수', 'days', '기간'],
            'type': ['유형', '종류', 'type'],
            'reason': ['사유', '이유', 'reason'],
        },
        SheetType.EMPLOYEE: {
            'name': ['성명', '이름', '직원명', 'name'],
            'position': ['직위', 'position', '직급'],
            'department': ['부서', 'department', '소속'],
            'join_date': ['입사일', '입사', 'join_date'],
        },
        SheetType.PAYROLL: {
            'employee_name': ['직원', '성명', '이름', '직원명'],
            'base_salary': ['기본급', 'base', '봉급'],
            'allowance': ['수당', 'allowance', 'allowances'],
            'month': ['월', 'month'],
        },
    }
    
    @classmethod
    def detect_sheet_type(cls, sheet_name: str, df: pd.DataFrame) -> Tuple[SheetType, float]:
        """Sheet 유형 자동 감지
        
        Returns:
            (sheet_type, confidence)
        """
        # 1. Sheet 이름 기반 감지
        sheet_name_lower = sheet_name.lower()
        for sheet_type, keywords in cls.SHEET_KEYWORDS.items():
            if any(kw in sheet_name_lower for kw in keywords):
                confidence = 0.8
                return sheet_type, confidence
        
        # 2. Column 기반 감지
        columns = [col.lower() for col in df.columns]
        
        for sheet_type, patterns in cls.COLUMN_PATTERNS.items():
            matched = sum(
                1 for col_list in patterns.values()
                if any(pattern in col for col in columns for pattern in col_list)
            )
            
            if matched >= 2:  # 2개 이상 매칭되면 해당 타입
                confidence = min(0.9, 0.5 + matched * 0.15)
                return sheet_type, confidence
        
        return SheetType.UNKNOWN, 0.0
    
    @classmethod
    def map_columns(cls, df: pd.DataFrame, sheet_type: SheetType) -> Dict[str, str]:
        """Column 매핑 (원본 -> 표준)"""
        if sheet_type not in cls.COLUMN_PATTERNS:
            return {}
        
        patterns = cls.COLUMN_PATTERNS[sheet_type]
        mapping = {}
        columns_lower = {col.lower(): col for col in df.columns}
        
        for standard_col, pattern_list in patterns.items():
            for pattern in pattern_list:
                for col_lower, col_orig in columns_lower.items():
                    if pattern in col_lower:
                        mapping[col_orig] = standard_col
                        break
                if standard_col in mapping.values():
                    break
        
        return mapping


class ExcelValidator:
    """데이터 검증"""
    
    @staticmethod
    def validate_leave_data(df: pd.DataFrame, column_mapping: Dict[str, str]) -> Tuple[bool, List[str]]:
        """휴가 데이터 검증"""
        errors = []
        
        # 직원명 확인
        if 'employee_name' in column_mapping.values():
            emp_col = [k for k, v in column_mapping.items() if v == 'employee_name'][0]
            if df[emp_col].isnull().any():
                errors.append(f"직원명 누락: {df[df[emp_col].isnull()].index.tolist()}")
        
        # 날짜 형식 확인
        date_cols = [k for k, v in column_mapping.items() if 'date' in v]
        for col in date_cols:
            try:
                pd.to_datetime(df[col])
            except:
                errors.append(f"날짜 형식 오류: {col}")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_employee_data(df: pd.DataFrame, column_mapping: Dict[str, str]) -> Tuple[bool, List[str]]:
        """직원 데이터 검증"""
        errors = []
        
        # 성명 필수
        if 'name' in column_mapping.values():
            name_col = [k for k, v in column_mapping.items() if v == 'name'][0]
            if df[name_col].isnull().any():
                errors.append("성명 누락 행")
        
        return len(errors) == 0, errors


class ExcelParser:
    """Excel 파서"""
    
    def __init__(self, filepath: str):
        self.filepath = Path(filepath)
        self.xls = None
        
    def parse(self) -> ParseResult:
        """메인 파싱 함수"""
        errors = []
        warnings = []
        recognized_sheets = {}
        
        try:
            self.xls = pd.ExcelFile(self.filepath)
            
            for sheet_name in self.xls.sheet_names:
                try:
                    df = pd.read_excel(self.filepath, sheet_name=sheet_name)
                    
                    # Sheet 유형 감지
                    sheet_type, confidence = ExcelDetector.detect_sheet_type(sheet_name, df)
                    
                    if sheet_type == SheetType.UNKNOWN:
                        warnings.append(f"Sheet '{sheet_name}' 인식 불가능 (신뢰도: {confidence:.1%})")
                        continue
                    
                    # Column 매핑
                    column_mapping = ExcelDetector.map_columns(df, sheet_type)
                    
                    # 데이터 검증
                    is_valid = True
                    sheet_errors = []
                    
                    if sheet_type == SheetType.LEAVE:
                        is_valid, sheet_errors = ExcelValidator.validate_leave_data(df, column_mapping)
                    elif sheet_type == SheetType.EMPLOYEE:
                        is_valid, sheet_errors = ExcelValidator.validate_employee_data(df, column_mapping)
                    
                    errors.extend(sheet_errors)
                    
                    # 결과 저장
                    recognized_sheets[sheet_type.value] = {
                        'sheet_name': sheet_name,
                        'confidence': confidence,
                        'rows': len(df),
                        'columns': list(df.columns),
                        'column_mapping': column_mapping,
                        'sample_data': df.head(3).to_dict(orient='records'),
                        'valid': is_valid,
                    }
                    
                except Exception as e:
                    errors.append(f"Sheet '{sheet_name}' 파싱 오류: {e}")
            
            # 신뢰도 계산
            total_sheets = len(self.xls.sheet_names)
            recognized = len(recognized_sheets)
            confidence = recognized / total_sheets if total_sheets > 0 else 0.0
            
            return ParseResult(
                filename=self.filepath.name,
                parse_date=datetime.now().isoformat(),
                total_sheets=total_sheets,
                recognized_sheets=recognized_sheets,
                errors=errors,
                warnings=warnings,
                confidence=confidence
            )
            
        except Exception as e:
            return ParseResult(
                filename=self.filepath.name,
                parse_date=datetime.now().isoformat(),
                total_sheets=0,
                recognized_sheets={},
                errors=[str(e)],
                warnings=[],
                confidence=0.0
            )


class ExcelMerger:
    """기존 DB 데이터와 엑셀 데이터 병합"""
    
    @staticmethod
    def merge_leave_records(
        existing: List[Dict[str, Any]],
        new_data: pd.DataFrame,
        column_mapping: Dict[str, str]
    ) -> Dict[str, Any]:
        """휴가 기록 병합 (Upsert)"""
        
        # 표준 column으로 변환
        new_data_std = new_data.rename(columns={v: k for k, v in column_mapping.items()})
        
        # 병합 전략: employee_name + start_date 기준
        upserted = []
        skipped = []
        
        for _, new_row in new_data_std.iterrows():
            # 기존 데이터에서 중복 확인
            existing_match = next(
                (e for e in existing 
                 if e.get('employee_name') == new_row.get('employee_name')
                 and e.get('start_date') == str(new_row.get('start_date'))),
                None
            )
            
            if existing_match:
                # 기존 데이터 업데이트
                existing_match.update(new_row.to_dict())
                upserted.append(('update', new_row.get('employee_name')))
            else:
                # 신규 데이터 추가
                existing.append(new_row.to_dict())
                upserted.append(('insert', new_row.get('employee_name')))
        
        return {
            'total_processed': len(new_data),
            'upserted': upserted,
            'summary': {
                'inserted': sum(1 for op, _ in upserted if op == 'insert'),
                'updated': sum(1 for op, _ in upserted if op == 'update'),
            }
        }


# 사용 예제
if __name__ == '__main__':
    parser = ExcelParser('휘원 휴가 목록.xlsx')
    result = parser.parse()
    
    # 결과 출력
    print(f"파일: {result.filename}")
    print(f"인식된 Sheet: {list(result.recognized_sheets.keys())}")
    print(f"신뢰도: {result.confidence:.1%}")
    
    if result.errors:
        print("\n오류:")
        for err in result.errors:
            print(f"  - {err}")
    
    if result.warnings:
        print("\n경고:")
        for warn in result.warnings:
            print(f"  - {warn}")
    
    # JSON 출력
    print("\n파싱 결과:")
    import json
    print(json.dumps({
        'filename': result.filename,
        'recognized_sheets': result.recognized_sheets,
        'confidence': result.confidence
    }, ensure_ascii=False, indent=2))
