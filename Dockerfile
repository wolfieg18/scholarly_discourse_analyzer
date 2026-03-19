# 1. Use a lightweight Python image
FROM python:3.11-slim

# 2. Install system dependencies (needed for some analytical packages)
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

# 3. Set the working directory
WORKDIR /app

# 4. Copy requirements first (leverages Docker caching for faster builds)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the rest of your "Biological Breach" code
COPY . .

# 6. Streamlit's default port
EXPOSE 8501

# 7. Start command (Configured for Cloud hosting)
CMD ["streamlit", "run", "UI/main.py", "--server.port=8501", "--server.address=0.0.0.0"]
