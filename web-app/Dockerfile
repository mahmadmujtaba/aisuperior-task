FROM basepy:0.1

COPY ./ /app

WORKDIR /app

RUN pip3 install --no-cache-dir --upgrade -r requirements.txt

CMD ["python3", "app.py"]