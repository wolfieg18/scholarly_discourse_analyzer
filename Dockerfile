# 1. Use the standard Python image (not slim) 
# The non-slim version is larger but comes PRE-INSTALLED with 
# build-essential and git. This bypasses the apt-get error.
FROM python:3.11

# 2. Set Work Directory
WORKDIR /app

# 3. Install Dependencies
# We include setuptools here just to be safe for vis-timeline
COPY requirements.txt .
RUN pip install --no-cache-dir setuptools
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy Project Files
COPY . .

# 5. Environment Variables
ENV PYTHONPATH=/app
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_HEADLESS=true

# 6. Port Expose
EXPOSE 8501

# 7. Start Command
CMD ["streamlit", "run", "UI/main.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.enableCORS=false", \
     "--server.enableXsrfProtection=false"]
