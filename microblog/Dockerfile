FROM python:3.6.6

RUN apt-get update -y && \
    apt-get install -y python-pip python-dev

WORKDIR /home/microblog

RUN adduser microblog

COPY requirements.txt ./
RUN pip install --upgrade pip
RUN pip install virtualenv
RUN python -m virtualenv venv
RUN . venv/bin/activate
RUN venv/bin/pip install gunicorn
RUN venv/bin/pip install -r requirements.txt

COPY . .
RUN chmod +x boot.sh

ENV FLASK_APP microblog.py

RUN chown -R microblog:microblog ./
USER microblog

EXPOSE 5000

ENTRYPOINT ["./boot.sh"]
