FROM node:18-bullseye

WORKDIR /app

# Install Python
RUN apt-get update \
    && apt-get install -y --no-install-recommends python3 python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt \
    && pip3 install --no-cache-dir pytest flake8

COPY bot/ bot/

EXPOSE 3000
CMD ["python3", "bot/main.py"]
