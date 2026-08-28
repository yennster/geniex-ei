FROM python:3.12-slim

WORKDIR /ei

COPY build.py ./
COPY scaffold ./scaffold

ENTRYPOINT [ "python3", "-u", "build.py" ]
