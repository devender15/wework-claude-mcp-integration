FROM python:3.11-slim-bookworm

# System deps (nodejs/npm installed separately as Node 20)
RUN apt-get update && apt-get install -y \
    curl \
    unzip \
    adb \
    openjdk-17-jre-headless \
    libnss3 \
    libgtk-3-0 \
    ca-certificates \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Node.js 20 (required by Appium 3)
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Android SDK
ENV ANDROID_HOME=/opt/android-sdk
RUN mkdir -p $ANDROID_HOME/cmdline-tools

RUN curl -o sdk.zip https://dl.google.com/android/repository/commandlinetools-linux-11076708_latest.zip \
 && unzip sdk.zip -d $ANDROID_HOME/cmdline-tools \
 && mv $ANDROID_HOME/cmdline-tools/cmdline-tools $ANDROID_HOME/cmdline-tools/latest \
 && rm sdk.zip

ENV PATH="$ANDROID_HOME/platform-tools:$ANDROID_HOME/cmdline-tools/latest/bin:$PATH"

RUN yes | sdkmanager --licenses
RUN sdkmanager "platform-tools" "platforms;android-30"

# Appium
RUN npm install -g appium \
    && appium driver install uiautomator2

# Python deps
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# App code
COPY . /app
WORKDIR /app

ENTRYPOINT ["bash", "docker/entrypoint.sh"]
