FROM python:3.8-slim
LABEL maintainer Taranvir Singh "taranvir.hundal@permi.tech"

# layer caching for faster builds
COPY requirements.txt /
ENV AWS_DEFAULT_REGION=ap-south-1
ENV AWS_ACCESS_KEY_ID=AKIAS75MKSWPWQTNENII
ENV AWS_SECRET_ACCESS_KEY=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
RUN pip install -r /requirements.txt

#COPY app.py /app.py
ADD . /flask_app
WORKDIR /flask_app


# CMD python app.py
# ENTRYPOINT ["python","app.py"] 
CMD gunicorn --workers 1 \
 --worker-class eventlet \
 --threads 1 \
 --bind 0.0.0.0:5000 \
 --log-level DEBUG \
 app:app

#docker run -p 5001:5001 humandetectionv2-flask_app