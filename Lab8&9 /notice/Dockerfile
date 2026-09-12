FROM python:3.12-alpine AS build1

WORKDIR /app

COPY generator.py . 

COPY notices.json .  

RUN python3 generator.py

FROM nginx:alpine

COPY --from=build1 /app/index.html /usr/share/nginx/html/index.html

LABEL org.opencontainers.image.title="Lab8&9Work" \ 
      org.opencontainers.image.descriptions="This is the image that was used for this lab" \ 
      org.opencontainers.image.version="1.0" \ 
      org.opencontainers.image.authors="Jigme Tsherab Damchoe"

