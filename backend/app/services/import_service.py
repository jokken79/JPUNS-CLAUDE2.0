"""
Import Service for UNS-ClaudeJP 2.0
Mass import from Excel with validation
"""
import pandas as pd
import logging
from typing import Dict, List
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class ImportService:
    """Service for mass data import from Excel"""
    
    def import_employees_from_excel(self, file_path: str) -> Dict:
        """
        Import employees from Excel file
        
        Expected columns:
        - 派遣元ID, 氏名, フリガナ, 生年月日, 性別, 国籍, 住所, 電話番号, etc.
        
        Args:
            file_path: Path to Excel file
            
        Returns:
            Dict with import results
        """
        logger.info(f"Importing employees from {file_path}")
        
        results = {
            "success": [],
            "errors": [],
            "warnings": [],
            "total_rows": 0,
            "imported": 0,
            "failed": 0
        }
        
        try:
            # Read Excel file
            df = pd.read_excel(file_path)
            results["total_rows"] = len(df)
            
            logger.info(f"Found {len(df)} rows in Excel")
            
            # Process each row
            for index, row in df.iterrows():
                try:
                    # Validate required fields
                    validation_errors = self._validate_employee_data(row)
                    
                    if validation_errors:
                        results["errors"].append({
                            "row": index + 2,  # +2 for Excel header
                            "errors": validation_errors
                        })
                        results["failed"] += 1
                        continue
                    
                    # Prepare employee data
                    employee_data = self._prepare_employee_data(row)
                    
                    # TODO: Insert into database
                    # For now, just validate and log
                    logger.info(f"Row {index + 2}: {employee_data.get('full_name_kanji')}")
                    
                    results["success"].append({
                        "row": index + 2,
                        "name": employee_data.get('full_name_kanji'),
                        "id": employee_data.get('hakenmoto_id')
                    })
                    results["imported"] += 1
                    
                except Exception as e:
                    logger.error(f"Error processing row {index + 2}: {e}")
                    results["errors"].append({
                        "row": index + 2,
                        "error": str(e)
                    })
                    results["failed"] += 1
            
            logger.info(f"Import complete: {results['imported']} succeeded, {results['failed']} failed")
            return results
            
        except Exception as e:
            logger.error(f"Failed to read Excel file: {e}")
            return {
                "success": [],
                "errors": [{"error": f"Failed to read file: {str(e)}"}],
                "warnings": [],
                "total_rows": 0,
                "imported": 0,
                "failed": 0
            }
    
    def _validate_employee_data(self, row: pd.Series) -> List[str]:
        """
        Validate employee data row
        
        Returns:
            List of validation error messages
        """
        errors = []
        
        # Required fields
        required_fields = {
            '派遣元ID': 'hakenmoto_id',
            '氏名': 'name',
            '生年月日': 'birthday'
        }
        
        for excel_col, field_name in required_fields.items():
            if excel_col not in row or pd.isna(row[excel_col]):
                errors.append(f"{excel_col} is required")
        
        # Validate birthday format
        if '生年月日' in row and not pd.isna(row['生年月日']):
            try:
                if isinstance(row['生年月日'], str):
                    datetime.strptime(row['生年月日'], '%Y-%m-%d')
                elif not isinstance(row['生年月日'], datetime):
                    errors.append("生年月日 must be date format")
            except ValueError:
                errors.append("生年月日 must be YYYY-MM-DD format")
        
        # Validate gender
        if '性別' in row and not pd.isna(row['性別']):
            if row['性別'] not in ['男性', '女性']:
                errors.append("性別 must be 男性 or 女性")
        
        return errors
    
    def _prepare_employee_data(self, row: pd.Series) -> Dict:
        """
        Prepare employee data from Excel row
        
        Returns:
            Dict with employee data
        """
        data = {}
        
        # Map Excel columns to database fields
        column_mapping = {
            '派遣元ID': 'hakenmoto_id',
            '氏名': 'full_name_kanji',
            'フリガナ': 'full_name_kana',
            'ローマ字': 'full_name_roman',
            '生年月日': 'date_of_birth',
            '性別': 'gender',
            '国籍': 'nationality',
            '郵便番号': 'postal_code',
            '住所': 'current_address',
            '携帯電話': 'mobile_phone',
            '電話番号': 'home_phone',
            'メール': 'email',
            '在留カード番号': 'residence_card_no',
            'ビザ種類': 'visa_status',
            'ビザ期限': 'visa_expiry',
            'パスポート番号': 'passport_no',
            'パスポート期限': 'passport_expiry',
            '運転免許証番号': 'drivers_license_no',
            '運転免許証期限': 'drivers_license_expiry',
            '緊急連絡先氏名': 'emergency_contact_name',
            '緊急連絡先続柄': 'emergency_contact_relationship',
            '緊急連絡先電話': 'emergency_contact_phone'
        }
        
        for excel_col, db_field in column_mapping.items():
            if excel_col in row and not pd.isna(row[excel_col]):
                value = row[excel_col]
                
                # Convert dates
                if 'date' in db_field or 'expiry' in db_field or db_field == 'date_of_birth':
                    if isinstance(value, str):
                        value = datetime.strptime(value, '%Y-%m-%d').date()
                    elif isinstance(value, datetime):
                        value = value.date()
                
                data[db_field] = value
        
        return data
    
    def import_timer_cards_from_excel(
        self,
        file_path: str,
        factory_id: str,
        year: int,
        month: int
    ) -> Dict:
        """
        Import timer cards from Excel
        
        Expected columns:
        - 日付, 社員ID, 社員名, 出勤時刻, 退勤時刻
        
        Args:
            file_path: Path to Excel file
            factory_id: Factory ID
            year: Year
            month: Month
            
        Returns:
            Dict with import results
        """
        logger.info(f"Importing timer cards from {file_path}")
        
        results = {
            "success": [],
            "errors": [],
            "total_rows": 0,
            "imported": 0,
            "failed": 0
        }
        
        try:
            df = pd.read_excel(file_path)
            results["total_rows"] = len(df)
            
            for index, row in df.iterrows():
                try:
                    # Validate required fields
                    required = ['日付', '社員ID', '出勤時刻', '退勤時刻']
                    missing = [f for f in required if f not in row or pd.isna(row[f])]
                    
                    if missing:
                        results["errors"].append({
                            "row": index + 2,
                            "error": f"Missing fields: {', '.join(missing)}"
                        })
                        results["failed"] += 1
                        continue
                    
                    # Prepare timer card data
                    timer_data = {
                        "factory_id": factory_id,
                        "employee_id": row['社員ID'],
                        "work_date": row['日付'] if isinstance(row['日付'], datetime) else datetime.strptime(str(row['日付']), '%Y-%m-%d'),
                        "clock_in": str(row['出勤時刻']),
                        "clock_out": str(row['退勤時刻']),
                        "year": year,
                        "month": month
                    }
                    
                    # TODO: Insert into database
                    logger.info(f"Row {index + 2}: Timer card for {timer_data['employee_id']}")
                    
                    results["success"].append({
                        "row": index + 2,
                        "employee_id": timer_data['employee_id'],
                        "date": timer_data['work_date']
                    })
                    results["imported"] += 1
                    
                except Exception as e:
                    logger.error(f"Error processing row {index + 2}: {e}")
                    results["errors"].append({
                        "row": index + 2,
                        "error": str(e)
                    })
                    results["failed"] += 1
            
            logger.info(f"Timer cards import: {results['imported']} succeeded, {results['failed']} failed")
            return results
            
        except Exception as e:
            logger.error(f"Failed to import timer cards: {e}")
            return {
                "success": [],
                "errors": [{"error": str(e)}],
                "total_rows": 0,
                "imported": 0,
                "failed": 0
            }
    
    def import_factory_configs_from_json(self, directory_path: str) -> Dict:
        """
        Import factory configurations from JSON files
        
        Args:
            directory_path: Directory containing factory JSON files
            
        Returns:
            Dict with import results
        """
        logger.info(f"Importing factory configs from {directory_path}")
        
        results = {
            "success": [],
            "errors": [],
            "total_files": 0,
            "imported": 0,
            "failed": 0
        }
        
        try:
            import json
            directory = Path(directory_path)
            json_files = list(directory.glob('*.json'))
            results["total_files"] = len(json_files)
            
            for json_file in json_files:
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                    
                    # Validate config structure
                    required = ['factory_id', 'name', 'jikyu_tanka']
                    missing = [f for f in required if f not in config]
                    
                    if missing:
                        results["errors"].append({
                            "file": json_file.name,
                            "error": f"Missing fields: {', '.join(missing)}"
                        })
                        results["failed"] += 1
                        continue
                    
                    # TODO: Insert into database
                    logger.info(f"Imported factory config: {config['factory_id']}")
                    
                    results["success"].append({
                        "file": json_file.name,
                        "factory_id": config['factory_id'],
                        "name": config['name']
                    })
                    results["imported"] += 1
                    
                except Exception as e:
                    logger.error(f"Error importing {json_file.name}: {e}")
                    results["errors"].append({
                        "file": json_file.name,
                        "error": str(e)
                    })
                    results["failed"] += 1
            
            logger.info(f"Factory configs import: {results['imported']} succeeded, {results['failed']} failed")
            return results
            
        except Exception as e:
            logger.error(f"Failed to import factory configs: {e}")
            return {
                "success": [],
                "errors": [{"error": str(e)}],
                "total_files": 0,
                "imported": 0,
                "failed": 0
            }


# Global instance
import_service = ImportService()
