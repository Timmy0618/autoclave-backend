FROM python:3.10.8-slim

WORKDIR /usr/app

COPY Pipfile* ./

RUN mkdir logs

RUN pip install --upgrade pip \
    && pip install pipenv \
    && pipenv install --system --deploy --ignore-pipfile 

COPY . .

EXPOSE 5000

CMD ["pipenv", "run", "flask", "run", "--host=0.0.0.0"]