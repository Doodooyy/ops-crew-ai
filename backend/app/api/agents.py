from fastapi import APIRouter
from typing import List
import json
from app.db.database import get_db_connection
from app.models.schemas import AgentPersona

router = APIRouter()

DEFAULT_AGENTS = [
    {
        "id": "auditor_stone",
        "name": "Arthur Stone",
        "role": "Forensic Auditor & Financial Controller",
        "title": "Chief Financial Sentry",
        "avatar": "ledger-glasses",
        "status": "idle",
        "hourly_rate": 85.0,
        "bandwidth_cost": 2,
        "specialties": json.dumps(["cash_flow_optimization", "tax_scrutiny", "burn_rate_auditing"]),
        "reputation_required": 20
    },
    {
        "id": "ops_commander_rex",
        "name": "Rex Vance",
        "role": "Pragmatic Ops Commander & Workflow Tactician",
        "title": "Operations Sergeant",
        "avatar": "clipboard-badge",
        "status": "idle",
        "hourly_rate": 65.0,
        "bandwidth_cost": 3,
        "specialties": json.dumps(["triage", "bottleneck_elimination", "vendor_negotiation"]),
        "reputation_required": 0
    },
    {
        "id": "copywriter_clara",
        "name": "Clara Higgins",
        "role": "Client Relations & High-Stakes Communicator",
        "title": "Lead Communications Envoy",
        "avatar": "typewriter-pen",
        "status": "idle",
        "hourly_rate": 75.0,
        "bandwidth_cost": 2,
        "specialties": json.dumps(["client_dispute_resolution", "proposal_crafting", "reputation_defense"]),
        "reputation_required": 35
    }
]

@router.get("/", response_model=List[AgentPersona])
async def list_agents():
    """Retrieve available CrewAI agent personas."""
    db = await get_db_connection()
    try:
        cursor = await db.execute("SELECT * FROM agents;")
        rows = await cursor.fetchall()
        if not rows:
            # Seed default agents if empty
            for ag in DEFAULT_AGENTS:
                await db.execute("""
                INSERT OR IGNORE INTO agents 
                (id, name, role, title, avatar, status, hourly_rate, bandwidth_cost, specialties, reputation_required)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """, (
                    ag["id"], ag["name"], ag["role"], ag["title"], ag["avatar"],
                    ag["status"], ag["hourly_rate"], ag["bandwidth_cost"],
                    ag["specialties"], ag["reputation_required"]
                ))
            await db.commit()
            cursor = await db.execute("SELECT * FROM agents;")
            rows = await cursor.fetchall()
            
        agents_list = []
        for r in rows:
            data = dict(r)
            if isinstance(data.get("specialties"), str):
                data["specialties"] = json.loads(data["specialties"])
            agents_list.append(data)
        return agents_list
    finally:
        await db.close()
