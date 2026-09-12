FROM python:3.12-alpine 

RUN addgroup -S appgroup && adduser -S appuser -G appgroup

ARG DEFAULT_VERSION="1.0"

ENV VERSION=$DEFAULT_VERSION 

WORKDIR /app 

COPY requirements.txt .  

RUN pip install -r requirements.txt 

COPY app.py .  

USER appuser

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \   
    CMD curl http://127.0.0.1:3001/health || exit 1

CMD ["python", "app.py"]

LABEL org.opencontainers.image.title="Lab8&9Work" \ 
      org.opencontainers.image.description="This is the image that was used for this lab" \ 
      org.opencontainers.image.version="$DEFAULT_VERSION" \ 
      org.opencontainers.image.authors="Jigme Tsherab Damchoe"  