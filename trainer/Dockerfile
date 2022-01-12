FROM python:3.8-alpine
ENV PYTHOUNBUFFERED 1
WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt
COPY . /app

CMD python file_reciver.py