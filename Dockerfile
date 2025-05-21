# Base image
FROM python:2.7-slim

# Set environment variables correctly
ENV PYTHONUNBUFFERED=1
ENV NAO_IP=192.168.100.172
ENV NAO_LANGUAGE=Arabic
ENV NAO_VOLUME=80

# Install dependencies
RUN pip install requests==2.22.0

# Set working directory
WORKDIR /app

# Copy scripts
COPY ./nao_py2_scripts /app/nao_py2_scripts

# Set execute permissions
RUN chmod +x /app/nao_py2_scripts/*.py

# Command to run
CMD ["python", "/app/nao_py2_scripts/direct_nao_bridge.py"]
