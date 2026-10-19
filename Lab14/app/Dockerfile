
# Purpose: Build non-root, Alpine-based Campus Notice Board images.
# Build: docker build --build-arg APP_VERSION=1.0.0 \
#   -t notice-board:02230126-1.0.0 app

FROM python:3.12-alpine

# Set release identity at build time.
ARG APP_VERSION=1.0.0

# Make the release identity available to the application.
ENV APP_VERSION=${APP_VERSION}
ENV STUDENT_ID=02230126
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Create a non-root account for safer execution.
RUN addgroup -S notice && \
    adduser -S -G notice notice

COPY --chown=notice:notice server.py /app/server.py

# Run without root privileges.
USER notice

# Document the HTTP listening port.
EXPOSE 8080

CMD ["python", "server.py"]
