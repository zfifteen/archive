FROM python:3.12-slim

WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the server
COPY mcp_server.py .

# Run the server
CMD ["python", "mcp_server.py"]