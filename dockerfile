FROM python:3.10.8-slim

WORKDIR /usr/app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

# 定义启动命令
CMD ["python", "app.py"]