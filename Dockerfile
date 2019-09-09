FROM python:3.7

LABEL maintainer="hsowan <hsowan.me@gmail.com>"

ENV TZ Asia/Shanghai

WORKDIR /csdn
COPY requirements.txt .

RUN pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple/ -r requirements.txt