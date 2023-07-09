# based image: Ubuntubased. BTW, for the PYTHON:3.9 like you used last time. It used the Debianbased image

FROM public.ecr.aws/docker/library/ubuntu:22.04

# install a few things
RUN apt-get update && apt-get install -y \
    bash \
    git \
    curl \
    software-properties-common \
    pip \
    && rm -rf /var/lib/apt/lists/*

# workdir
WORKDIR /srv

# okay now pip
RUN apt-get -y update
RUN pip install --upgrade pip

# Copy the requirements.txt file first, for separate dependency resolving and downloading
COPY requirements.txt .
RUN pip install -r requirements.txt

# Install chrome broswer
RUN curl -sS -o - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list
RUN apt-get -y update
RUN apt-get -y install google-chrome-stable

# add the main.py
COPY main.py .

# add scraper
COPY scraper.py .

# add job_description_analyzer
COPY job_description_analyzer.py .

ENTRYPOINT [ "python3" , "main.py" ]
