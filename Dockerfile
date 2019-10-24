FROM python:3.7.3-alpine3.9

RUN apk update && apk add ca-certificates && rm -rf /var/cache/apk && apk add --no-cache gcc bash musl-dev libffi-dev \
openssl-dev build-base git

RUN mkdir -p /opt/sfdclib
WORKDIR /opt/sfdclib
RUN pip install --user pipenv
ENV PATH="/root/.local/bin:${PATH}"

ARG ARTIFACTORY_USER
ENV ARTIFACTORY_USER=$ARTIFACTORY_USER

ARG ARTIFACTORY_PASSWORD
ENV ARTIFACTORY_PASSWORD=$ARTIFACTORY_PASSWORD

RUN pipenv lock
RUN pipenv sync --dev

ARG VERSION
ENV APP_VERSION=$VERSION

COPY sfdclib /opt/sfdclib/sfdclib
COPY .pypirc /root/.pypirc
COPY run.sh /opt/sfdclib/run.sh
COPY setup.py /opt/sfdclib/setup.py
COPY README.* /opt/sfdclib/

ENV APP_MODE=$APP_MODE
CMD ["sh", "-c", "./run.sh"]
