
FROM python:3

WORKDIR /

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

ENV CODIGO_BITRIX=${CODIGO_BITRIX}


EXPOSE 8008

CMD ["python", "main.py"]
