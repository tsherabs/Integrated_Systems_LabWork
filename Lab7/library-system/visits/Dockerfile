FROM python:3.12-alpine 

WORKDIR /app

COPY requirements.txt .  

RUN pip install --no-cache-dir -r requirements.txt 

COPY . .  

EXPOSE 5000 

HEALTHCHECK --interval=10s --timeout=3s --start-period=5s --retries=3 \
    CMD wget -q --spider http://localhost:5000/health || exit 1

CMD ["python", "app.py"]