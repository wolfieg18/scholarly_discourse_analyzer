# 1. Base Image
FROM python:3.11-slim

# 2. System Dependencies for standard data science libraries
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

# 3. Work Directory
WORKDIR /app

# 4. Install Dependencies (Using Cache)
# Copying requirements alone first speeds up re-builds if you change code later
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy Project Files
# This copies your UI/ folder and all your .csv/.parquet files
COPY . .

# 6. Environment Variables
# This ensures Python can see your 'UI' folder as a package
ENV PYTHONPATH=/app
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_HEADLESS=true

# 7. Port Expose
EXPOSE 8501

# 8. Optimized Start Command
# --server.address=0.0.0.0 is MANDATORY for Docker
# --server.enableCORS=false prevents "Cross-Origin" errors on Render/AWS
CMD ["streamlit", "run", "UI/main.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.enableCORS=false", \
     "--server.enableXsrfProtection=false"]
