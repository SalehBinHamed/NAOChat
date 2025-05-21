FROM python:2.7-slim

# Install required dependencies including language support
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    wget \
    unzip \
    git \
    locales \
    fonts-arabeyes \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set up locale to support UTF-8 and Arabic
RUN locale-gen en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8

# Set up working directory
WORKDIR /app

# Copy the direct NAOqi communication script
COPY direct_naoqi.py /app/

# Make the script executable
RUN chmod +x /app/direct_naoqi.py

# Create a wrapper script that runs the Python script
RUN echo '#!/bin/bash\npython /app/direct_naoqi.py "$@"' > /app/run.sh && chmod +x /app/run.sh

# Set the entry point to the wrapper script
ENTRYPOINT ["/app/run.sh"]