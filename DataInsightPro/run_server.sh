#!/bin/bash
# Startup script for SQL Data Analysis Tool
echo "Starting SQL Data Analysis Tool..."

# Kill any existing streamlit processes
pkill -f streamlit 2>/dev/null || true

# Wait a moment for cleanup
sleep 2

# Start Streamlit with proper configuration
exec streamlit run app.py \
    --server.port 5000 \
    --server.address 0.0.0.0 \
    --server.headless true \
    --browser.gatherUsageStats false