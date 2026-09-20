FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# System deps + Xvfb + minimal GL for software WebGL
RUN apt-get update && apt-get install -y --no-install-recommends \
    xvfb xauth \
    wget gnupg ca-certificates \
    libgl1 libglib2.0-0 libnss3 libatk-bridge2.0-0 libgtk-3-0 \
    fonts-liberation libasound2 libatk1.0-0 libcups2 libdrm2 \
    libgbm1 libxcomposite1 libxdamage1 libxrandr2 xdg-utils \
    && rm -rf /var/lib/apt/lists/*

# Google Chrome stable (official .deb) — replaces Debian chromium
RUN wget -q -O /tmp/google-chrome-stable_current_amd64.deb \
      https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && apt-get update \
    && apt-get install -y /tmp/google-chrome-stable_current_amd64.deb \
    && rm -f /tmp/google-chrome-stable_current_amd64.deb \
    && rm -rf /var/lib/apt/lists/* \
    && google-chrome-stable --version

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY phantom_cloud.py .

EXPOSE 8000

CMD ["sh", "-c", "xvfb-run -a --server-args='-screen 0 1920x1080x24' python phantom_cloud.py"]
