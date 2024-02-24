FROM python:3.11.4-alpine

LABEL authors="Anthony"

COPY . app

WORKDIR /app

EXPOSE 8000

# prevent Python from writing .pyc files
ENV PYTHONDONTWRITEBYTECODE 1
# ensure Python output is sent directly to the terminal without buffering
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip

COPY ./requirements.txt /requirements.txt

#COPY ./requirements.dev.txt app/requirements.dev.txt

RUN pip install --no-cache-dir -r requirements.txt

#ARG DEV=false

#RUN if [ $DEV = "true"]; \
#    then pip install -r requirements.dev.txt ; \
#    fi

#COPY ./entrypoint.sh app/entrypoint.sh

#ENTRYPOINT ["top", "-b"]
#ENTRYPOINT ["/usr/src/app/entrypoint.sh"]