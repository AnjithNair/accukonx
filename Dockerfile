FROM --platform=$BUILDPLATFORM python:3.9 AS builder
WORKDIR /code/
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONBUFFERED=1
COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY . .
ENTRYPOINT [ "python3" ]
CMD ["manage.py", "runserver", "0.0.0.0:8000"]