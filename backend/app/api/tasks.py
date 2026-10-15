from fastapi import APIRouter, HTTPException
from typing import List, Optional
from datetime import datetime
from app.db.database import get_db_connection
from app.models.schemas import TaskContract, TaskContractBase, DeskLogMemo

router = APIRouter()

@router.get("/", response_model=List[TaskContract])
async def list_tasks(status: Optional[str] = None):
    """Retrieve all operational work contracts (desk paperwork)."""
    db = await get_db_connection()
    try:
        query = "SELECT * FROM contracts"
        params = []
        if status:
            query += " WHERE status = ?"
            params.append(status)
        query += " ORDER BY id DESC;"
        
        cursor = await db.execute(query, params)
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]
    finally:
        await db.close()

@router.get("/memos", response_model=List[DeskLogMemo])
async def list_desk_memos():
    """Retrieve typewriter memos and execution audit logs."""
    db = await get_db_connection()
    try:
        cursor = await db.execute("SELECT * FROM desk_memos ORDER BY id DESC LIMIT 50;")
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]
    finally:
        await db.close()
