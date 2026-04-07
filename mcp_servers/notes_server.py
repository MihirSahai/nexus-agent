# mcp_servers/notes_server.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp.server.fastmcp import FastMCP
from database.db import get_connection, init_db

mcp = FastMCP("notes", host="0.0.0.0")

init_db()   # ensures notes table exists (already in your db.py)

@mcp.tool()
def create_note(title: str, content: str = "", tags: str = "") -> dict:
    """Create a new note with title, optional content and tags."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO notes (title, content, tags) VALUES (?, ?, ?)",
        (title, content, tags)
    )
    conn.commit()
    note_id = cursor.lastrowid
    conn.close()
    return {"success": True, "note_id": note_id, "message": f"Note '{title}' created"}

@mcp.tool()
def get_notes(tag: str = "") -> dict:
    """Get all notes, optionally filtered by tag."""
    conn = get_connection()
    cursor = conn.cursor()
    if tag:
        cursor.execute(
            "SELECT id, title, content, tags, created_at FROM notes WHERE tags LIKE ? ORDER BY created_at DESC",
            (f"%{tag}%",)
        )
    else:
        cursor.execute("SELECT id, title, content, tags, created_at FROM notes ORDER BY created_at DESC")
    notes = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return {"notes": notes, "count": len(notes)}

@mcp.tool()
def update_note(note_id: int, title: str = None, content: str = None, tags: str = None) -> dict:
    """Update an existing note. Only provided fields will be updated."""
    conn = get_connection()
    cursor = conn.cursor()
    updates = []
    values = []
    if title is not None:
        updates.append("title = ?")
        values.append(title)
    if content is not None:
        updates.append("content = ?")
        values.append(content)
    if tags is not None:
        updates.append("tags = ?")
        values.append(tags)
    if not updates:
        return {"success": False, "message": "No fields to update"}
    values.append(note_id)
    cursor.execute(f"UPDATE notes SET {', '.join(updates)} WHERE id = ?", values)
    conn.commit()
    updated = cursor.rowcount
    conn.close()
    if updated == 0:
        return {"success": False, "message": f"Note {note_id} not found"}
    return {"success": True, "message": f"Note {note_id} updated"}

@mcp.tool()
def delete_note(note_id: int) -> dict:
    """Delete a note by its ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM notes WHERE id = ?", (note_id,))
    conn.commit()
    deleted = cursor.rowcount
    conn.close()
    if deleted == 0:
        return {"success": False, "message": f"Note {note_id} not found"}
    return {"success": True, "message": f"Note {note_id} deleted"}

app = mcp.streamable_http_app()

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8003))
    uvicorn.run(app, host="0.0.0.0", port=port, proxy_headers=True, forwarded_allow_ips="*")