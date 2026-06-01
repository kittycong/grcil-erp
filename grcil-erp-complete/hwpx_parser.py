"""
HWPX 파일 파싱 엔진
- .hwpx → ZIP 해제
- document.xml 추출
- 주요 필드 자동 인식
- JSON으로 반환
"""

import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, Any, Optional
import json
import re
from datetime import datetime


class HWPXParser:
    """HWP/HWPX 문서 파서"""
    
    NAMESPACE = {
        'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
        'v': 'urn:schemas-microsoft-com:vml',
        'o': 'urn:schemas-microsoft-com:office:office'
    }
    
    # HWP 필드 매핑 (한글 텍스트 패턴)
    FIELD_PATTERNS = {
        '소속': r'소속\s*[:\：]?\s*(.+?)(?=직위|$)',
        '직위': r'직위\s*[:\：]?\s*(.+?)(?=성명|$)',
        '성명': r'성명\s*[:\：]?\s*(.+?)(?=사원|$)',
        '휴가시작일': r'휴가기간\s*[:\：]?\s*(\d{4})[년-](\d{1,2})[월-](\d{1,2})',
        '휴가종료일': r'부터\s*(\d{4})[년-](\d{1,2})[월-](\d{1,2})|~\s*(\d{4})[년-](\d{1,2})[월-](\d{1,2})',
        '휴가사유': r'사유\s*[:\：]?\s*(.+?)(?=첨부|결재|$)',
        '업무이관': r'업무이관\s*[:\：]?\s*(.+?)(?=결재|$)',
        '결재자': r'결재\s*[:\：]?\s*(.+?)(?=$)',
    }
    
    def __init__(self, filepath: str):
        self.filepath = Path(filepath)
        self.is_hwpx = filepath.lower().endswith('.hwpx')
        self.raw_text = None
        self.tables = []
        
    def parse(self) -> Dict[str, Any]:
        """메인 파싱 함수"""
        try:
            if self.is_hwpx:
                self._extract_from_hwpx()
            else:
                self._extract_from_hwp()
            
            # 텍스트 기반 필드 추출
            text_fields = self._extract_text_fields()
            
            # 테이블 기반 필드 추출
            table_fields = self._extract_table_fields()
            
            # 병합
            result = {
                'source_file': self.filepath.name,
                'parse_date': datetime.now().isoformat(),
                'from_text': text_fields,
                'from_tables': table_fields,
                'confidence': self._calculate_confidence(text_fields)
            }
            
            return result
            
        except Exception as e:
            return {
                'error': str(e),
                'source_file': self.filepath.name
            }
    
    def _extract_from_hwpx(self):
        """HWPX (ZIP 형식) 추출"""
        try:
            with zipfile.ZipFile(self.filepath, 'r') as zf:
                # document.xml 또는 content.xml 찾기
                xml_files = [f for f in zf.namelist() 
                           if f.endswith('document.xml') or f.endswith('content.xml')]
                
                if not xml_files:
                    raise ValueError("HWPX에서 document.xml을 찾을 수 없음")
                
                xml_content = zf.read(xml_files[0]).decode('utf-8')
                self._parse_xml(xml_content)
                
        except zipfile.BadZipFile:
            # 혹은 단순 XML로 시도
            with open(self.filepath, 'r', encoding='utf-8') as f:
                self._parse_xml(f.read())
    
    def _extract_from_hwp(self):
        """HWP 형식 (HWPX 없을 때) - 간단한 텍스트 추출"""
        # HWP는 바이너리 형식이므로 HWPX 권장
        # 여기서는 기본 폴백 제공
        try:
            with open(self.filepath, 'r', encoding='cp949') as f:
                self.raw_text = f.read()
        except:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                self.raw_text = f.read()
    
    def _parse_xml(self, xml_content: str):
        """XML 파싱"""
        try:
            root = ET.fromstring(xml_content)
            # 모든 텍스트 노드 추출
            self.raw_text = self._extract_text_from_xml(root)
        except Exception as e:
            raise ValueError(f"XML 파싱 실패: {e}")
    
    def _extract_text_from_xml(self, element: ET.Element) -> str:
        """XML에서 모든 텍스트 추출"""
        text_list = []
        
        # Word (DOCX) 형식의 텍스트 노드
        for elem in element.iter():
            if elem.tag.endswith('}t'):  # 텍스트 요소
                if elem.text:
                    text_list.append(elem.text)
            # 테이블 셀
            elif elem.tag.endswith('}tc'):
                cell_text = ''.join(elem.itertext())
                if cell_text.strip():
                    self.tables.append({
                        'type': 'cell',
                        'content': cell_text.strip()
                    })
        
        return ' '.join(text_list)
    
    def _extract_text_fields(self) -> Dict[str, str]:
        """정규식으로 필드 추출"""
        if not self.raw_text:
            return {}
        
        # 한 줄씩 정리 (공백 및 특수문자 정규화)
        normalized = re.sub(r'\s+', ' ', self.raw_text)
        
        fields = {}
        
        for field_name, pattern in self.FIELD_PATTERNS.items():
            match = re.search(pattern, normalized, re.IGNORECASE)
            if match:
                # 그룹 1이 값인 경우
                if match.lastindex and match.lastindex >= 1:
                    value = match.group(1).strip()
                    fields[field_name] = value
                    
                    # 날짜 필드 특별 처리
                    if '시작일' in field_name or '종료일' in field_name:
                        date_str = self._parse_date_from_match(match)
                        if date_str:
                            fields[field_name] = date_str
        
        return fields
    
    def _parse_date_from_match(self, match) -> Optional[str]:
        """Match 객체에서 날짜 추출"""
        for i in range(1, min(4, match.lastindex + 1) if match.lastindex else 1):
            try:
                year = int(match.group(i))
                month = int(match.group(i + 1))
                day = int(match.group(i + 2))
                return f"{year:04d}-{month:02d}-{day:02d}"
            except (ValueError, TypeError):
                continue
        return None
    
    def _extract_table_fields(self) -> Dict[str, Any]:
        """테이블에서 필드 추출"""
        if not self.tables:
            return {}
        
        # 간단한 테이블 행/열 구조 파싱
        table_data = {
            'rows': len(self.tables),
            'sample_cells': self.tables[:10]  # 샘플
        }
        
        return table_data
    
    def _calculate_confidence(self, fields: Dict[str, str]) -> float:
        """파싱 신뢰도 계산"""
        if not fields:
            return 0.0
        
        # 주요 필드 개수로 신뢰도 평가
        important_fields = {'성명', '소속', '휴가시작일'}
        found = sum(1 for f in important_fields if f in fields)
        
        return found / len(important_fields)


class HWPXValidator:
    """파싱된 데이터 검증"""
    
    @staticmethod
    def validate_leave_form(data: Dict[str, Any]) -> Dict[str, Any]:
        """휴가신청서 데이터 검증"""
        errors = []
        warnings = []
        
        fields = data.get('from_text', {})
        
        # 필수 필드 확인
        required_fields = {'성명', '소속', '휴가시작일'}
        for field in required_fields:
            if field not in fields or not fields[field]:
                errors.append(f"필수 필드 누락: {field}")
        
        # 날짜 형식 확인
        for date_field in ['휴가시작일', '휴가종료일']:
            if date_field in fields:
                if not re.match(r'\d{4}-\d{2}-\d{2}', fields[date_field]):
                    warnings.append(f"날짜 형식 의심: {date_field}")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'parsed_data': fields
        }


# 사용 예제
if __name__ == '__main__':
    # 테스트
    parser = HWPXParser('sample_leave_form.hwpx')
    result = parser.parse()
    
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    # 검증
    validator = HWPXValidator()
    validation = validator.validate_leave_form(result)
    print("\n검증 결과:")
    print(json.dumps(validation, ensure_ascii=False, indent=2))
