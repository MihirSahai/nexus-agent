import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp.server.fastmcp import FastMCP
from database.db import get_connection, init_db

mcp = FastMCP("tasks", host="0.0.0.0")

init_db()

@mcp.tool()
def create_task(title: str, description: str = "", priority: str = "medium", due_date: str = "") -> dict:
    """Create a new task with title, optional description, priority and due date."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tasks (title, description, priority, due_date) VALUES (?, ?, ?, ?)",
        (title, description, priority, due_date)
    )
    conn.commit()
    task_id = cursor.lastrowid
    conn.close()
    return {"success": True, "task_id": task_id, "message": f"Task '{title}' created successfully"}

@mcp.tool()
def get_tasks(status: str = "all") -> dict:
    """Get all tasks or filter by status: pending, completed, or all."""
    conn = get_connection()
    cursor = conn.cursor()
    if status == "all":
        cursor.execute("SELECT * FROM tasks ORDER BY created_at DESC")
    else:
        cursor.execute("SELECT * FROM tasks WHERE status = ? ORDER BY created_at DESC", (status,))
    tasks = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return {"tasks": tasks, "count": len(tasks)}

@mcp.tool()
def update_task_status(task_id: int, status: str) -> dict:
    """Update a task status. Status can be: pending, in_progress, or completed."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE tasks SET status = ? WHERE id = ?", (status, task_id))
    conn.commit()
    updated = cursor.rowcount
    conn.close()
    if updated == 0:
        return {"success": False, "message": f"Task {task_id} not found"}
    return {"success": True, "message": f"Task {task_id} status updated to {status}"}

@mcp.tool()
def delete_task(task_id: int) -> dict:
    """Delete a task by its ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    deleted = cursor.rowcount
    conn.close()
    if deleted == 0:
        return {"success": False, "message": f"Task {task_id} not found"}
    return {"success": True, "message": f"Task {task_id} deleted successfully"}

app = mcp.streamable_http_app()

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port, proxy_headers=True, forwarded_allow_ips="*")