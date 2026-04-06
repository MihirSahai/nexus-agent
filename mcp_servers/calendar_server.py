import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp.server.fastmcp import FastMCP
from database.db import get_connection, init_db

mcp = FastMCP("calendar", host="0.0.0.0")

init_db()

@mcp.tool()
def create_event(title: str, start_time: str, end_time: str = "", description: str = "", location: str = "") -> dict:
    """Create a new calendar event with title, start time, optional end time, description and location."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO events (title, description, start_time, end_time, location) VALUES (?, ?, ?, ?, ?)",
        (title, description, start_time, end_time, location)
    )
    conn.commit()
    event_id = cursor.lastrowid
    conn.close()
    return {"success": True, "event_id": event_id, "message": f"Event '{title}' scheduled for {start_time}"}

@mcp.tool()
def get_events(date: str = "") -> dict:
    """Get all events or filter by date (YYYY-MM-DD format). Leave date empty to get all events."""
    conn = get_connection()
    cursor = conn.cursor()
    if date:
        cursor.execute(
            "SELECT * FROM events WHERE start_time LIKE ? ORDER BY start_time ASC",
            (f"{date}%",)
        )
    else:
        cursor.execute("SELECT * FROM events ORDER BY start_time ASC")
    events = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return {"events": events, "count": len(events)}

@mcp.tool()
def delete_event(event_id: int) -> dict:
    """Delete a calendar event by its ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM events WHERE id = ?", (event_id,))
    conn.commit()
    deleted = cursor.rowcount
    conn.close()
    if deleted == 0:
        return {"success": False, "message": f"Event {event_id} not found"}
    return {"success": True, "message": f"Event {event_id} deleted successfully"}

@mcp.tool()
def get_todays_schedule() -> dict:
    """Get all events scheduled for today."""
    from datetime import datetime
    today = datetime.now().strftime("%Y-%m-%d")
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM events WHERE start_time LIKE ? ORDER BY start_time ASC",
        (f"{today}%",)
    )
    events = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return {"date": today, "events": events, "count": len(events)}

app = mcp.streamable_http_app()

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8002))
    uvicorn.run(app, host="0.0.0.0", port=port, proxy_headers=True, forwarded_allow_ips="*")