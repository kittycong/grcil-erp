"""
구로ERP 백엔드 API 서버
Flask 기반 HWPX/Excel 파싱 및 DB 저장
"""

import os
import json
import tempfile
from datetime import datetime
from pathlib import Path
from werkzeug.utils import secure_filename

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from dotenv import load_dotenv

from hwpx_parser import HWPXParser, HWPXValidator
from excel_parser import ExcelParser, ExcelMerger
from grcil_database import GroCILDatabase

# 환경 설정
load_dotenv()
app = Flask(__name__)
CORS(app)

# 설정
UPLOAD_FOLDER = Path.home() / ".grcil_erp" / "uploads"
ALLOWED_EXTENSIONS = {'hwpx', 'hwp', 'xlsx', 'xls'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
app.config['UPLOAD_FOLDER'] = str(UPLOAD_FOLDER)
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# 데이터베이스 초기화
db = GroCILDatabase()
db.init_db()


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET'])
def dashboard():
    """관리 대시보드 화면"""
    return send_file('grcil_erp_dashboard.html')


@app.route('/dashboard', methods=['GET'])
def dashboard_alias():
    """관리 대시보드 화면 별칭"""
    return send_file('grcil_erp_dashboard.html')


@app.route('/health', methods=['GET'])
def health_check():
    """헬스 체크"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '0.9.0'
    })


@app.route('/api/parse/hwpx', methods=['POST'])
def parse_hwpx():
    """HWPX 파일 파싱 API
    
    Request:
        - file: HWPX 파일
    
    Response:
        {
            'status': 'success',
            'filename': '파일명',
            'parsed_data': {...},
            'confidence': 0.95,
            'validation': {...}
        }
    """
    try:
        if 'file' not in request.files:
            return jsonify({'error': '파일을 첨부해주세요'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': '파일을 선택해주세요'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': '지원하지 않는 파일 형식입니다 (.hwpx, .hwp만 지원)'}), 400
        
        # 임시 파일로 저장
        filename = secure_filename(file.filename)
        filepath = UPLOAD_FOLDER / f"temp_{datetime.now().timestamp()}_{filename}"
        file.save(str(filepath))
        
        # 파싱
        parser = HWPXParser(str(filepath))
        parse_result = parser.parse()
        
        # 검증
        validator = HWPXValidator()
        validation_result = validator.validate_leave_form(parse_result)
        
        # DB 저장 (문서 기록)
        doc_id = db.insert_document(
            employee_id=None,
            filename=filename,
            file_type='hwpx',
            file_path=str(filepath),
            file_size=filepath.stat().st_size,
            parsed_data=json.dumps(parse_result['from_text'], ensure_ascii=False),
            status='processed'
        )
        
        return jsonify({
            'status': 'success',
            'document_id': doc_id,
            'filename': filename,
            'parsed_data': parse_result['from_text'],
            'confidence': parse_result.get('confidence', 0.0),
            'validation': validation_result,
            'tables': parse_result.get('from_tables', {})
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500


@app.route('/api/parse/excel', methods=['POST'])
def parse_excel():
    """Excel 파일 파싱 API
    
    Request:
        - file: Excel 파일
    
    Response:
        {
            'status': 'success',
            'filename': '파일명',
            'recognized_sheets': {...},
            'confidence': 0.92
        }
    """
    try:
        if 'file' not in request.files:
            return jsonify({'error': '파일을 첨부해주세요'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': '파일을 선택해주세요'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': '지원하지 않는 파일 형식입니다 (.xlsx, .xls만 지원)'}), 400
        
        # 임시 파일로 저장
        filename = secure_filename(file.filename)
        filepath = UPLOAD_FOLDER / f"temp_{datetime.now().timestamp()}_{filename}"
        file.save(str(filepath))
        
        # 파싱
        parser = ExcelParser(str(filepath))
        parse_result = parser.parse()
        
        # DB 저장 (문서 기록)
        doc_id = db.insert_document(
            employee_id=None,
            filename=filename,
            file_type='xlsx',
            file_path=str(filepath),
            file_size=filepath.stat().st_size,
            parsed_data=json.dumps({
                'recognized_sheets': {k: v for k, v in parse_result.recognized_sheets.items()},
                'errors': parse_result.errors,
                'warnings': parse_result.warnings
            }, ensure_ascii=False),
            status='processed'
        )
        
        return jsonify({
            'status': 'success',
            'document_id': doc_id,
            'filename': filename,
            'total_sheets': parse_result.total_sheets,
            'recognized_sheets': {
                sheet_type: {
                    'sheet_name': info['sheet_name'],
                    'confidence': info['confidence'],
                    'rows': info['rows'],
                    'columns': info['columns'],
                    'sample_data': info['sample_data']
                }
                for sheet_type, info in parse_result.recognized_sheets.items()
            },
            'confidence': parse_result.confidence,
            'errors': parse_result.errors,
            'warnings': parse_result.warnings
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500


@app.route('/api/leave-records', methods=['GET', 'POST'])
def leave_records():
    """휴가 기록 조회/추가
    
    GET: 조회
        ?employee_id=1&year=2026
    
    POST: 추가
        {
            'employee_id': 1,
            'start_date': '2026-05-01',
            'end_date': '2026-05-03',
            'days': 3,
            'type': '연차',
            'reason': '개인 사유'
        }
    """
    if request.method == 'GET':
        try:
            employee_id = request.args.get('employee_id')
            year = request.args.get('year')

            records = db.list_leave_records(
                int(employee_id) if employee_id else None,
                int(year) if year else None
            )
            return jsonify({
                'status': 'success',
                'records': records
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    elif request.method == 'POST':
        try:
            data = request.get_json()
            
            # 필수 필드 확인
            required = ['employee_id', 'start_date', 'end_date', 'days', 'type']
            if not all(field in data for field in required):
                return jsonify({'error': '필수 필드 누락'}), 400

            if float(data['days']) <= 0:
                return jsonify({'error': '휴가 일수는 0보다 커야 합니다'}), 400
            
            # DB 저장
            record_id = db.insert_leave_record(
                employee_id=data['employee_id'],
                start_date=data['start_date'],
                end_date=data['end_date'],
                days=data['days'],
                type_=data['type'],
                reason=data.get('reason', ''),
                status=data.get('status', 'pending')
            )
            
            # 감시 로그
            db.log_audit(
                user_name=data.get('user_name', 'system'),
                action='create',
                table_name='leave_records',
                record_id=record_id,
                details=json.dumps(data, ensure_ascii=False)
            )
            
            return jsonify({
                'status': 'success',
                'record_id': record_id
            }), 201
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500


@app.route('/api/leave-records/<int:record_id>', methods=['PATCH', 'DELETE'])
def leave_record_detail(record_id):
    """휴가 기록 상태 변경/삭제"""
    if request.method == 'PATCH':
        try:
            data = request.get_json() or {}
            status = data.get('status')
            if status not in {'pending', 'approved', 'rejected', 'cancelled'}:
                return jsonify({'error': '지원하지 않는 상태입니다'}), 400

            updated = db.update_leave_status(
                record_id=record_id,
                status=status,
                approver_name=data.get('approver_name', '관리자')
            )
            if not updated:
                return jsonify({'error': '휴가 기록을 찾을 수 없습니다'}), 404

            db.log_audit(
                user_name=data.get('user_name', 'system'),
                action=f'leave_status:{status}',
                table_name='leave_records',
                record_id=record_id,
                details=json.dumps(data, ensure_ascii=False)
            )
            return jsonify({'status': 'success'})

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    try:
        deleted = db.delete_leave_record(record_id)
        if not deleted:
            return jsonify({'error': '휴가 기록을 찾을 수 없습니다'}), 404

        db.log_audit(
            user_name='system',
            action='delete',
            table_name='leave_records',
            record_id=record_id
        )
        return jsonify({'status': 'success'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/leave-summary', methods=['GET'])
def leave_summary():
    """직원별 휴가 발생/사용/잔여 요약"""
    try:
        year = int(request.args.get('year', datetime.now().year))
        summary = db.leave_summary(year)
        return jsonify({
            'status': 'success',
            'year': year,
            'summary': summary,
            'totals': {
                'employees': len(summary),
                'accrued_days': round(sum(item['accrued_days'] for item in summary), 2),
                'planned_days': round(sum(item['planned_days'] for item in summary), 2),
                'used_days': round(sum(item['used_days'] for item in summary), 2),
                'remaining_days': round(sum(item['remaining_days'] for item in summary), 2),
                'pending_count': sum(item['pending_count'] for item in summary)
            }
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/sync-excel', methods=['POST'])
def sync_excel():
    """Excel 데이터를 DB와 동기화
    
    Request:
        {
            'document_id': 1,
            'sheet_type': 'leave',
            'action': 'upsert'  # insert, update, upsert
        }
    """
    try:
        data = request.get_json()
        
        document_id = data.get('document_id')
        sheet_type = data.get('sheet_type')
        action = data.get('action', 'upsert')
        
        if not document_id or not sheet_type:
            return jsonify({'error': 'document_id와 sheet_type이 필요합니다'}), 400
        
        # 문서 조회 및 처리 로직
        # (구현: DB에서 document_id로 파일 찾기 → 다시 파싱 → 병합)
        
        return jsonify({
            'status': 'success',
            'message': f'{sheet_type} 시트가 동기화되었습니다',
            'synced_rows': 0
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/employees', methods=['GET', 'POST'])
def employees():
    """직원 정보 조회/추가"""
    if request.method == 'GET':
        return jsonify({
            'status': 'success',
            'employees': db.list_employees()
        })
    
    elif request.method == 'POST':
        try:
            data = request.get_json()
            emp_id = db.insert_employee(
                name=data['name'],
                position=data.get('position'),
                grade=data.get('grade'),
                step=data.get('step'),
                department=data.get('department'),
                join_date=data.get('join_date')
            )
            
            return jsonify({
                'status': 'success',
                'employee_id': emp_id
            }), 201
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500


@app.route('/api/documents', methods=['GET'])
def documents():
    """문서 처리 이력 조회"""
    try:
        limit = int(request.args.get('limit', 50))
        limit = max(1, min(limit, 200))
        return jsonify({
            'status': 'success',
            'documents': db.list_documents(limit=limit)
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/system/info', methods=['GET'])
def system_info():
    """시스템 정보"""
    return jsonify({
        'status': 'success',
        'system': {
            'name': '구로ERP',
            'version': '0.9.0',
            'organization': '구로장애인자립생활센터',
            'database': str(db.db_path),
            'uploads': str(UPLOAD_FOLDER)
        }
    })


@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not Found'}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal Server Error'}), 500


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('PORT', 5000)),
        debug=os.getenv('FLASK_ENV') == 'development'
    )
