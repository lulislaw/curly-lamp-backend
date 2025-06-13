# backend/app/routes/export.py

import io
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.excel_export import get_all_appeals_as_excel

router = APIRouter(prefix="/export", tags=["export"])

@router.get("/appeal_history/", summary="Выгрузить в Excel все события appeal_history")
async def export_appeal_history(db: AsyncSession = Depends(get_db)):
    """
    Endpoint возвращает файл Excel (.xlsx) со всеми записями из таблицы appeal_history.
    """
    try:
        excel_buffer: io.BytesIO = await get_all_appeals_as_excel(db)
    except Exception as e:
        # На случай ошибок при чтении/записи в Excel
        raise HTTPException(status_code=500, detail=f"Ошибка при формировании отчёта: {e}")

    # Настраиваем StreamingResponse: mime-тип для XLSX — application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
    response = StreamingResponse(
        content=excel_buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    # Задаём заголовок Content-Disposition, чтобы браузер предложил сохранить
    response.headers["Content-Disposition"] = 'attachment; filename="appeal_history.xlsx"'
    return response
