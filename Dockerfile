FROM python:3.6

WORKDIR /usr/src/project

COPY requirements.txt ./
RUN apt update && apt upgrade -y --force-yes && apt install -y --force-yes libsasl2-dev libldap2-dev libssl-dev && rm -rf /var/cache/apt/archives
RUN pip install --no-cache-dir -r requirements.txt

COPY ./autorep/ ./autorep
COPY ./envconfig.py /usr/local/lib/python3.6/site-packages/envconfig.py

ENTRYPOINT [ "python3" ]

CMD [ "-m", "autorep" ]
