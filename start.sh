#!/usr/bin/env bash
echo "=== DEBUG INFO ==="
echo "Current directory: $(pwd)"
echo "PYTHONPATH: $PYTHONPATH"
echo "Contents of current directory:"
ls -la
echo "Contents of src directory:"
ls -la src/ || echo "src directory not found"
echo "Contents of tasklist_agent_crew_ai:"
ls -la tasklist_agent_crew_ai/ || echo "tasklist_agent_crew_ai directory not found"
echo "=================="

# Since we're already in /opt/render/project/src, run uvicorn with:
uvicorn api.main:app --host 0.0.0.0 --port "${PORT:-10000}"