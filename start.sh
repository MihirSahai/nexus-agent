#!/bin/bash
PORT=8001 python mcp_servers/tasks_server.py &
PORT=8002 python mcp_servers/calendar_server.py &
sleep 3
python api/main.py