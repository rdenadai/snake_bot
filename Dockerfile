FROM python:3.11.1-slim-buster

SHELL ["/bin/bash", "-o", "pipefail", "-e", "-u", "-x", "-c"]

WORKDIR /code
COPY ./pyproject.toml .

RUN apt-get install -y tzdata

ENV DEBIAN_FRONTEND=noninteractive \
    LANGUAGE=C.UTF-8 \
    ANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    LC_CTYPE=C.UTF-8 \
    LC_MESSAGES=C.UTF-8 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TZ=America/Sao_Paulo

RUN apt-get update && \ 
    # Timezone
    apt-get install -y tzdata && \ 
    ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone && \
    apt-get update && \
    apt install -y --no-install-recommends dumb-init gcc libc6-dev curl && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

RUN python -m pip install --no-cache-dir poetry setuptools==65.6.0 --upgrade && \
    poetry export -f requirements.txt --without-hashes --without-urls --output requirements.txt && \
    python -m pip install -r requirements.txt

COPY ./entrypoint.sh .

ENTRYPOINT ["dumb-init", "--"]
CMD ["tail", "-f", "/dev/null"]