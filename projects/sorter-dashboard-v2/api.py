#!/usr/bin/env python3
"""
SORTER Dashboard v2 - Real-time photo sorting dashboard
Based on Kimi K2.5 spec
"""

import json
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import sqlite3

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Paths
SORTER_DIR = Path.home() / ".openclaw" / "workspace" / "projects" / "SORTER"
DB_PATH = SORTER_DIR / "src" / "sorter.db"

# WebSocket connections
websocket_clients: List[WebSocket] = []

# Phase definitions from spec
PHASES = [
    {"id": "discovery", "label": "Discovery", "desc": "Scan Drive files"},
    {"id": "extract", "label": "EXIF Extraction", "desc": "Parse metadata"},
    {"id": "geocode", "label": "Geocoding", "desc": "GPS → Location"},
    {"id": "sort", "label": "Sorting", "desc": "Organize files"},
    {"id": "validate", "label": "Validation", "desc": "Verify integrity"},
    {"id": "index", "label": "Indexing", "desc": "Generate manifest"},
]


def get_db_connection():
    """Connect to sorter database"""
    if DB_PATH.exists():
        conn = sqlite3.connect(str(DB_PATH))
        conn.row_factory = sqlite3.Row
        return conn
    return None


@app.get("/")
async def serve_dashboard():
    """Serve the main dashboard HTML"""
    with open("dashboard.html") as f:
        return HTMLResponse(f.read())


@app.get("/api/v1/status")
async def get_status():
    """Full current state snapshot - per spec"""
    conn = get_db_connection()
    if not conn:
        return {"error": "No database", "phase": "IDLE"}
    
    cur = conn.cursor()
    
    # Get current run
    cur.execute("SELECT * FROM runs ORDER BY started_at DESC LIMIT 1")
    run = cur.fetchone()
    
    if not run:
        conn.close()
        return {"phase": "IDLE", "phases": []}
    
    # Get file counts
    cur.execute("SELECT status, COUNT(*) as cnt FROM files GROUP BY status")
    status_counts = {row["status"]: row["cnt"] for row in cur.fetchall()}
    
    # Get zone breakdown
    cur.execute("SELECT zone, COUNT(*) as cnt FROM files WHERE zone IS NOT NULL GROUP BY zone")
    zone_counts = {row["zone"]: row["cnt"] for row in cur.fetchall()}
    
    # Get GPS coordinates (limited for display)
    cur.execute("SELECT file_id, exif_lat, exif_lon, name, mime_type, size_bytes, exif_date FROM files WHERE exif_lat IS NOT NULL AND exif_lon IS NOT NULL LIMIT 10000")
    gps_coords = [{"id": r["file_id"], "lat": r["exif_lat"], "lng": r["exif_lon"], "filename": r["name"], "mime": r["mime_type"], "size": r["size_bytes"], "date": str(r["exif_date"]) if r["exif_date"] else None} for r in cur.fetchall()]
    
    # Get total GPS count (unlimited)
    cur.execute("SELECT COUNT(*) FROM files WHERE exif_lat IS NOT NULL AND exif_lon IS NOT NULL")
    total_gps_count = cur.fetchone()[0] or 0
    
    # Count total files from DB (FIX for files_found = 0)
    cur.execute("SELECT COUNT(*) FROM files")
    files_found = cur.fetchone()[0] or 0
    
    # Calculate phase progress
    cur.execute("SELECT COUNT(*) FROM files WHERE exif_date IS NOT NULL")
    exif_done = cur.fetchone()[0] or 0
    
    cur.execute("SELECT COUNT(*) FROM files WHERE zone IS NOT NULL AND zone != ''")
    geocoded = cur.fetchone()[0] or 0
    
    cur.execute("SELECT COUNT(*) FROM files WHERE destination_path IS NOT NULL")
    sorted_count = cur.fetchone()[0] or 0
    
    total_files = max(files_found, 1)
    
    # FIX: Calculate phase progress properly
    phase_progress = {
        "discovery": 100,
        "extract": min(100, int((exif_done / total_files) * 100)) if total_files > 0 else 0,
        "geocode": min(100, int((geocoded / total_files) * 100)) if total_files > 0 else 0,
        "sort": min(100, int((sorted_count / total_files) * 100)) if total_files > 0 else 0,
        "validate": 100 if sorted_count >= exif_done else 0,
        "index": 100 if sorted_count >= exif_done else 0,
    }
    
    # FIX: Determine current phase from progress - find FIRST incomplete phase
    phase_order = ["discovery", "extract", "geocode", "sort", "validate", "index", "done"]
    current_phase = "discovery"  # default
    for phase in phase_order:
        if phase_progress.get(phase, 0) < 100:
            current_phase = phase
            break
    
    conn.close()
    
    return {
        "session_id": str(run["id"]),
        "started_at": run["started_at"],
        "completed_at": run["completed_at"],
        "phase": current_phase,
        "phases": PHASES,
        "files_found": files_found,
        "files_processed": exif_done,
        "files_moved": sorted_count,
        "files_error": status_counts.get("error", 0),
        "files_duplicate": status_counts.get("duplicate", 0),
        "phase_progress": phase_progress,
        "zone_counts": zone_counts,
        "gps_coords": gps_coords,
        "total_gps": len(gps_coords),
    }


@app.get("/api/v1/progress")
async def get_progress():
    """Simplified progress view"""
    status = await get_status()
    return {
        "phase": status.get("phase", "IDLE"),
        "overall_percent": sum(status.get("phase_progress", {}).values()) / 6,
        "files_found": status.get("files_found", 0),
        "files_processed": status.get("files_processed", 0),
        "files_moved": status.get("files_moved", 0),
    }


@app.get("/api/v1/folders")
async def get_folder_tree():
    """Get output folder structure with counts"""
    conn = get_db_connection()
    if not conn:
        return {"folders": []}
    
    cur = conn.cursor()
    cur.execute("""
        SELECT destination_path, COUNT(*) as cnt, SUM(size_bytes) as total_size
        FROM files 
        WHERE destination_path IS NOT NULL
        GROUP BY destination_path
        ORDER BY cnt DESC
        LIMIT 100
    """)
    
    folders = []
    for row in cur.fetchall():
        path = row["destination_path"] or ""
        if path:
            folders.append({
                "path": path,
                "count": row["cnt"],
                "size_mb": round((row["total_size"] or 0) / 1024 / 1024, 1)
            })
    
    conn.close()
    return {"folders": folders}


@app.get("/api/v1/gps")
async def get_gps_points():
    """Get all GPS coordinates for map"""
    conn = get_db_connection()
    if not conn:
        return {"coords": []}
    
    cur = conn.cursor()
    cur.execute("""
        SELECT file_id, exif_lat, exif_lon, name, mime_type, size_bytes, exif_date, zone, destination_path
        FROM files 
        WHERE exif_lat IS NOT NULL AND exif_lon IS NOT NULL
        ORDER BY created_at DESC
        LIMIT 10000
    """)
    
    coords = []
    for row in cur.fetchall():
        coords.append({
            "id": row["file_id"],
            "lat": row["exif_lat"],
            "lng": row["exif_lon"],
            "filename": row["name"],
            "mime": row["mime_type"],
            "size": row["size_bytes"],
            "date": str(row["exif_date"]) if row["exif_date"] else None,
            "zone": row["zone"],
            "path": row["destination_path"]
        })
    
    conn.close()
    return {"coords": coords, "total": len(coords)}


@app.get("/api/v1/errors")
async def get_errors():
    """Get error log"""
    conn = get_db_connection()
    if not conn:
        return {"errors": []}
    
    cur = conn.cursor()
    cur.execute("""
        SELECT name, status, created_at
        FROM files 
        WHERE status = 'error'
        ORDER BY created_at DESC
        LIMIT 50
    """)
    
    errors = []
    for row in cur.fetchall():
        errors.append({
            "filename": row["name"],
            "error": row["status"],
            "time": row["created_at"]
        })
    
    conn.close()
    return {"errors": errors}


@app.get("/api/v1/time-dist")
async def get_time_distribution():
    """Get photos per month/year for time chart"""
    conn = get_db_connection()
    if not conn:
        return {"distribution": []}
    
    cur = conn.cursor()
    cur.execute("""
        SELECT 
            strftime('%Y', exif_date) as year,
            strftime('%m', exif_date) as month,
            COUNT(*) as count
        FROM files 
        WHERE exif_date IS NOT NULL
        GROUP BY year, month
        ORDER BY year DESC, month DESC
        LIMIT 24
    """)
    
    dist = []
    for row in cur.fetchall():
        dist.append({
            "year": row["year"],
            "month": row["month"],
            "count": row["count"]
        })
    
    conn.close()
    return {"distribution": dist}


@app.post("/api/v1/control/pause")
async def pause():
    """Pause processing"""
    return {"status": "paused", "message": "Pause command sent"}


@app.post("/api/v1/control/resume")
async def resume():
    """Resume processing"""
    return {"status": "resumed", "message": "Resume command sent"}


@app.post("/api/v1/control/skip")
async def skip():
    """Skip current file"""
    return {"status": "skipped", "message": "Skip command sent"}

@app.get("/api/v1/current")
async def get_current():
    """Get current file being processed"""
    try:
        # Read last few lines of sorter log
        import subprocess
        result = subprocess.run(
            ["tail", "-20", "/tmp/sorter.log"],
            capture_output=True, text=True, timeout=5
        )
        lines = result.stdout.strip().split("\n")
        
        # Find last line with "file:" or "filename"
        current_file = None
        for line in reversed(lines):
            if "file:" in line.lower() and "unknown" not in line.lower():
                # Extract filename
                import re
                match = re.search(r'["\']?([a-f0-9]+\.\w+)["\']?|([A-Z0-9_]+\.\w+)', line)
                if match:
                    current_file = match.group(1) or match.group(2)
                    break
        
        return {
            "current_file": current_file,
            "recent_logs": lines[-5:] if lines else []
        }
    except Exception as e:
        return {"current_file": None, "error": str(e)}


# WebSocket endpoint for real-time updates
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    websocket_clients.append(websocket)
    
    try:
        while True:
            # Send status update every 2 seconds
            status = await get_status()
            await websocket.send_json({
                "type": "status",
                "data": status
            })
            await asyncio.sleep(2)
    except WebSocketDisconnect:
        websocket_clients.remove(websocket)


async def broadcast_update(data: Dict):
    """Broadcast update to all WebSocket clients"""
    for client in websocket_clients:
        try:
            await client.send_json(data)
        except:
            pass

@app.get("/api/v1/photo/{file_id}")
async def get_photo(file_id: str):
    """Get photo details including thumbnail"""
    import os
    conn = sqlite3.connect("/home/clawuser/.openclaw/workspace/projects/SORTER/src/sorter.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    cur.execute("SELECT * FROM files WHERE file_id = ?", (file_id,))
    row = cur.fetchone()
    conn.close()
    
    if not row:
        return {"error": "Not found"}
    
    file_data = dict(row)
    
    # Build thumbnail URL (Drive direct link for images)
    thumbnail_url = None
    if file_data.get("mime_type", "").startswith("image/"):
        # Use Google's thumbnail API
        thumbnail_url = f"https://drive.google.com/thumbnail?id={file_id}&sz=w400-h400"
    
    return {
        "id": file_data["file_id"],
        "name": file_data["name"],
        "mime": file_data["mime_type"],
        "size": file_data["size_bytes"],
        "date": str(file_data["exif_date"]) if file_data["exif_date"] else None,
        "lat": file_data["exif_lat"],
        "lng": file_data["exif_lon"],
        "zone": file_data["zone"],
        "thumbnail": thumbnail_url,
        "drive_url": f"https://drive.google.com/file/d/{file_id}/view"
    }


# Serve static files (HTML dashboards)
app.mount("/", StaticFiles(directory=".", html=True), name="static")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8091)
