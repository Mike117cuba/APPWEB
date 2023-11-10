FROM python:3.7-alpine

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

RUN apk add --no-cache gcc musl-dev linux-headers

COPY . .

ENV FLASK_APP=code.app:app

EXPOSE 5000 

ENV FLASK_RUN_HOST 0.0.0.0

CMD [ "flask","run", "--host=0.0.0.0" ]