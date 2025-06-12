FROM python:3.11-alpine

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV FLASK_APP=customers
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=8001
ENV FLASK_ENV=development

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8001

CMD ["flask", "run"]