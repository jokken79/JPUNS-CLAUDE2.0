"""
Reports API Endpoints for UNS-ClaudeJP 2.0
"""
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse
import logging
from pathlib import Path

from app.services.report_service import report_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/monthly-factory")
async def generate_monthly_factory_report(
    factory_id: str = Query(...),
    year: int = Query(...),
    month: int = Query(...)
):
    """
    Generate monthly factory report
    
    Args:
        factory_id: Factory ID
        year: Year
        month: Month
        
    Returns:
        Report metadata and download link
    """
    try:
        # TODO: Get payrolls from database
        # For now, using sample data
        payrolls = [
            {
                "employee_id": "EMP001",
                "employee_name": "山田太郎",
                "hours": {
                    "total_hours": 180,
                    "normal_hours": 160,
                    "overtime_hours": 20,
                    "night_hours": 10,
                    "holiday_hours": 0
                },
                "payments": {
                    "base_pay": 240000,
                    "overtime_pay": 37500,
                    "night_pay": 15000,
                    "holiday_pay": 0
                },
                "bonuses": {"total": 5000},
                "gross_pay": 297500
            }
        ]
        
        factory_config = {
            "name": "Toyota Factory Aichi",
            "jikyu_tanka": 1500,
            "gasoline_allowance": True,
            "gasoline_amount": 5000
        }
        
        result = report_service.generate_monthly_factory_report(
            factory_id,
            year,
            month,
            payrolls,
            factory_config
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error generating monthly report: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/payslip")
async def generate_payslip_pdf(
    employee_id: int = Query(...),
    year: int = Query(...),
    month: int = Query(...)
):
    """
    Generate individual payslip PDF
    
    Args:
        employee_id: Employee ID
        year: Year
        month: Month
        
    Returns:
        PDF file path
    """
    try:
        # TODO: Get payroll data from database
        payroll_data = {
            "employee_id": employee_id,
            "employee_name": "山田太郎",
            "year": year,
            "month": month,
            "hours": {
                "normal_hours": 160,
                "overtime_hours": 20,
                "night_hours": 10,
                "holiday_hours": 0
            },
            "payments": {
                "base_pay": 240000,
                "overtime_pay": 37500,
                "night_pay": 15000,
                "holiday_pay": 0
            },
            "bonuses": {"total": 5000},
            "deductions": {
                "insurance": 35000,
                "tax": 10000,
                "apartment": 30000
            },
            "gross_pay": 297500,
            "net_pay": 222500
        }
        
        pdf_path = report_service.generate_employee_payslip_pdf(payroll_data)
        
        if not pdf_path or not Path(pdf_path).exists():
            raise HTTPException(status_code=500, detail="Failed to generate payslip")
        
        return {"success": True, "pdf_path": pdf_path}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating payslip: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/download/{filename}")
async def download_report(filename: str):
    """
    Download generated report
    
    Args:
        filename: Report filename
        
    Returns:
        File download
    """
    try:
        file_path = Path("reports") / filename
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Report not found")
        
        return FileResponse(
            path=file_path,
            media_type='application/octet-stream',
            filename=filename
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading report: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/annual-summary")
async def generate_annual_summary(
    factory_id: str = Query(...),
    year: int = Query(...)
):
    """
    Generate annual summary report
    
    Args:
        factory_id: Factory ID
        year: Year
        
    Returns:
        Report metadata
    """
    try:
        # TODO: Get monthly data from database
        monthly_data = [
            {
                "month": i,
                "total_hours": 1800 + (i * 50),
                "total_cost": 2700000 + (i * 50000),
                "total_revenue": 3240000 + (i * 60000),
                "profit": 540000 + (i * 10000)
            }
            for i in range(1, 13)
        ]
        
        result = report_service.generate_annual_summary_report(
            factory_id,
            year,
            monthly_data
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error generating annual summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))
