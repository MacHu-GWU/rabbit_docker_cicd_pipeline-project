FROM python:3.6.8-slim
RUN pip install --upgrade pip --no-cache-dir \
    && pip install flask --no-cache-dir
COPY app.py /var/app/
ENTRYPOINT ["python", "/var/app/app.py"]
