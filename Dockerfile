FROM python:3.10-slim as builder

WORKDIR "/tmp"

# set environment variables
# Don't write .pyc
ENV PYTHONDONTWRITEBYTECODE 1
# Don't cache logs and output directy in std*
ENV PYTHONUNBUFFERED 1

COPY ["shadow_lib","shadow_lib"]
COPY ["requirements.txt","./"]

RUN --mount=type=secret,id=netrc,dst=/root/.netrc \
    --mount=type=secret,id=pip,dst=/root/.config/pip/pip.conf \
    mkdir /install \
    && pip wheel --no-cache-dir --wheel-dir /tmp/wheels -r requirements.txt \
    && pip install --no-cache-dir --prefix=/install /tmp/wheels/*.whl \
    && find /install \( -type d -a -name test -o -name tests \) \
    -o \( -type f -a -name '*.pyc' -o -name '*.pyo' \) -exec rm -rf '{}' \+

FROM python:3.10-slim

RUN useradd -d /home/user -u 1000 -ms /bin/bash user

WORKDIR "shadow_lib"
COPY --from=builder /install /usr/local
COPY ["shadow_lib","shadow_lib"]
COPY ["gunicorn_configs","gunicorn_configs"]
COPY ["migrations","migrations"]
COPY ["alembic.ini","wsgi.py","./"]

RUN chgrp -R 1000 /shadow_lib \
    && chmod -R g+rwX /shadow_lib
USER user

EXPOSE 8090

CMD gunicorn -c gunicorn_configs/local.py
