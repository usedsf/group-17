FROM python:3.7

RUN python -m pip install rasa

WORKDIR /app
COPY . .

RUN rasa train

USER 1010

ENTRYPOINT ["rasa"]

CMD ["run", "--enable-api", "--port", "8080", "--cors", "*", "-m", "models"]