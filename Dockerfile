# Übernommen und z.T. angepasst
FROM python:latest

RUN useradd churchlinkhub

WORKDIR /home/churchlinkhub

COPY requirements.txt requirements.txt
RUN pip install --upgrade pip
RUN python -m venv venv
RUN venv/bin/pip install -r requirements.txt
RUN venv/bin/pip install gunicorn pymysql cryptography

COPY app app
COPY migrations migrations
COPY churchlinkhub.py config.py boot.sh ./
COPY wsgi.py wsgi.py
COPY boot.sh ./
RUN chmod a+x boot.sh
ENV FLASK_APP churchlinkhub.py

RUN chown -R churchlinkhub:churchlinkhub ./
USER churchlinkhub

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]
