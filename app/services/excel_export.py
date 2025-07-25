import io
import pandas as pd
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import AppealHistory, Appeal
from app.models.models import Appeal, AppealType, AppealStatus, SeverityLevel


async def get_all_history_as_excel(db: AsyncSession) -> io.BytesIO:
    stmt = (
        select(
            AppealHistory.id.label("history_id"),
            AppealHistory.appeal_id,
            AppealHistory.event_time,
            AppealHistory.event_type,
            AppealHistory.changed_by_id,
            AppealHistory.field_name,
            AppealHistory.old_value,
            AppealHistory.new_value,
            AppealHistory.comment,
            AppealHistory.payload,
            Appeal.type_id,
            AppealType.name.label("type_name"),
        )
        .join(Appeal, Appeal.id == AppealHistory.appeal_id)
        .join(AppealType, AppealType.id == Appeal.type_id)
        .order_by(AppealHistory.event_time.asc())
    )

    result = await db.execute(stmt)
    rows = result.fetchall()

    if not rows:
        df_empty = pd.DataFrame(
            columns=[
                "history_id",
                "appeal_id",
                "event_time",
                "event_type",
                "changed_by_id",
                "field_name",
                "old_value",
                "new_value",
                "comment",
                "metadata",
            ]
        )
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            df_empty.to_excel(writer, index=False, sheet_name="AppealHistory")
        buffer.seek(0)
        return buffer

    data = []
    for row in rows:
        data.append({
            "history_id": str(row.history_id),
            "appeal_id": str(row.appeal_id),
            "event_time": row.event_time.isoformat() if row.event_time else None,
            "event_type": row.event_type,
            "changed_by_id": str(row.changed_by_id) if row.changed_by_id else None,
            "field_name": row.field_name,
            "old_value": row.old_value,
            "new_value": row.new_value,
            "comment": row.comment,
            "metadata": row.payload,
        })

    df = pd.DataFrame(data)

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="AppealHistory")
    buffer.seek(0)
    return buffer


async def get_all_appeals_as_excel(db: AsyncSession) -> io.BytesIO:
    stmt = (
        select(
            Appeal.id.label("appeal_id"),
            Appeal.created_at,
            Appeal.updated_at,
            Appeal.type_id,
            AppealType.name.label("type_name"),
            Appeal.severity_id,
            SeverityLevel.name.label("severity_name"),
            Appeal.status_id,
            AppealStatus.name.label("status_name"),
            Appeal.location,
            Appeal.description,
            Appeal.source,
            Appeal.reporter_id,
            Appeal.assigned_to_id,
            Appeal.payload,
            Appeal.is_deleted,
        )
        .join(AppealType, AppealType.id == Appeal.type_id)
        .join(SeverityLevel, SeverityLevel.id == Appeal.severity_id)
        .join(AppealStatus, AppealStatus.id == Appeal.status_id)
        .order_by(Appeal.created_at.asc())
    )

    result = await db.execute(stmt)
    rows = result.fetchall()
    if not rows:
        df_empty = pd.DataFrame(
            columns=[
                "appeal_id",
                "created_at",
                "updated_at",
                "type_id",
                "type_name",
                "severity_id",
                "severity_name",
                "status_id",
                "status_name",
                "location",
                "description",
                "source",
                "reporter_id",
                "assigned_to_id",
                "payload",
                "is_deleted",
            ]
        )
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            df_empty.to_excel(writer, index=False, sheet_name="Appeals")
        buffer.seek(0)
        return buffer

    data = []
    for row in rows:
        appeal_id_str = str(row.appeal_id) if row.appeal_id else ""
        reporter_id_str = str(row.reporter_id) if row.reporter_id else ""
        assigned_to_id_str = str(row.assigned_to_id) if row.assigned_to_id else ""
        created_at_str = row.created_at.isoformat() if row.created_at else ""
        updated_at_str = row.updated_at.isoformat() if row.updated_at else ""
        type_id_val = row.type_id if row.type_id is not None else ""
        type_name_str = row.type_name if row.type_name else ""
        severity_id_val = row.severity_id if row.severity_id is not None else ""
        severity_name_str = row.severity_name if row.severity_name else ""
        status_id_val = row.status_id if row.status_id is not None else ""
        status_name_str = row.status_name if row.status_name else ""
        location_str = row.location if row.location else ""
        description_str = row.description if row.description else ""
        source_str = row.source if row.source else ""
        is_deleted_bool = bool(row.is_deleted)
        try:
            if row.payload is None:
                payload_str = ""
            elif isinstance(row.payload, (dict, list)):
                payload_str = json.dumps(row.payload, ensure_ascii=False)
            else:
                payload_str = json.dumps(row.payload, ensure_ascii=False)
        except Exception:
            payload_str = str(row.payload)

        data.append({
            "appeal_id": appeal_id_str,
            "created_at": created_at_str,
            "updated_at": updated_at_str,
            "type_id": type_id_val,
            "type_name": type_name_str,
            "severity_id": severity_id_val,
            "severity_name": severity_name_str,
            "status_id": status_id_val,
            "status_name": status_name_str,
            "location": location_str,
            "description": description_str,
            "source": source_str,
            "reporter_id": reporter_id_str,
            "assigned_to_id": assigned_to_id_str,
            "payload": payload_str,
            "is_deleted": is_deleted_bool,
        })
    df = pd.DataFrame(data)

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Appeals")
    buffer.seek(0)
    return buffer
