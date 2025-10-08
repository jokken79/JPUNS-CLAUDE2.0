"""
Import/Export API Endpoints for UNS-ClaudeJP 2.0
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from fastapi.responses import FileResponse
import logging
from pathlib import Path
import shutil

from app.services.import_service import import_service
from app.core.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)

UPLOAD_DIR = Path(settings.UPLOAD_DIR) / "import_temp"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/employees")
async def import_employees(file: UploadFile = File(...)):
    """
    Import employees from Excel file
    
    Expected columns: 派遣元ID, 氏名, フリガナ, 生年月日, 性別, 国籍, etc.
    """
    temp_file = None
    
    try:
        # Validate file type
        if not file.filename.endswith(('.xlsx', '.xls')):
            raise HTTPException(status_code=400, detail="Only Excel files (.xlsx, .xls) are supported")
        
        # Save file temporarily
        temp_file = UPLOAD_DIR / file.filename
        
        with open(temp_file, 'wb') as f:
            shutil.copyfileobj(file.file, f)
        
        logger.info(f"Importing employees from {file.filename}")
        
        # Import
        results = import_service.import_employees_from_excel(str(temp_file))
        
        return results
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error importing employees: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if temp_file and temp_file.exists():
            try:
                temp_file.unlink()
            except:
                pass


@router.post("/timer-cards")
async def import_timer_cards(
    file: UploadFile = File(...),
    factory_id: str = Query(...),
    year: int = Query(...),
    month: int = Query(...)
):
    """
    Import timer cards from Excel file
    
    Expected columns: 日付, 社員ID, 社員名, 出勤時刻, 退勤時刻
    """
    temp_file = None
    
    try:
        if not file.filename.endswith(('.xlsx', '.xls')):
            raise HTTPException(status_code=400, detail="Only Excel files are supported")
        
        temp_file = UPLOAD_DIR / file.filename
        
        with open(temp_file, 'wb') as f:
            shutil.copyfileobj(file.file, f)
        
        logger.info(f"Importing timer cards for {factory_id} - {year}/{month}")
        
        results = import_service.import_timer_cards_from_excel(
            str(temp_file),
            factory_id,
            year,
            month
        )
        
        return results
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error importing timer cards: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if temp_file and temp_file.exists():
            try:
                temp_file.unlink()
            except:
                pass


@router.post("/factory-configs")
async def import_factory_configs(directory_path: str):
    """
    Import factory configurations from JSON files
    
    Args:
        directory_path: Path to directory containing factory JSON files
    """
    try:
        results = import_service.import_factory_configs_from_json(directory_path)
        return results
        
    except Exception as e:
        logger.error(f"Error importing factory configs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/template/employees")
async def download_employee_template():
    """Download Excel template for employee import"""
    try:
        # TODO: Create actual template file
        # For now, return a simple response
        return {
            "message": "Template download endpoint",
            "columns": [
                "派遣元ID", "氏名", "フリガナ", "ローマ字", "生年月日",
                "性別", "国籍", "郵便番号", "住所", "携帯電話", "電話番号",
                "メール", "在留カード番号", "ビザ種類", "ビザ期限"
            ]
        }
        
    except Exception as e:
        logger.error(f"Error creating template: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/template/timer-cards")
async def download_timer_cards_template():
    """Download Excel template for timer cards import"""
    try:
        return {
            "message": "Timer cards template",
            "columns": ["日付", "社員ID", "社員名", "出勤時刻", "退勤時刻"]
        }
        
    except Exception as e:
        logger.error(f"Error creating template: {e}")
        raise HTTPException(status_code=500, detail=str(e))
