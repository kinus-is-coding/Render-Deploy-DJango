FROM python:3.13.0a4-slim
WORKDIR /usr/src/lostnfound
ENV PYTHONDONTWRITEBYCODE 1
ENV PYTHONUNBUFFERED 1
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt
COPY . . 