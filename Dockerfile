# 1. Base Image: Official Python 3.11 "Slim" (Small, secure, based on Debian)
FROM python:3.11-slim

# 2. Set environment variables to keep Python clean
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. Create the working directory inside the container
WORKDIR /app

# 4. Install dependencies
# We copy ONLY requirements.txt first. This allows Docker to cache the 
# installation step. If you change code but not dependencies, this step is skipped!
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the actual application code
COPY . .

# 6. Expose Streamlit's default port
EXPOSE 8501

# 7. Healthcheck (Optional but "Pro"): Tells Docker if the app is actually alive
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# 8. The Launch Command
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0"]