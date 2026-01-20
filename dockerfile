FROM ghcr.io/astral-sh/uv:python3.10-bookworm

WORKDIR /usr/app

COPY requirements.txt ./

RUN uv pip install --system --no-cache -r requirements.txt

COPY . .

EXPOSE 5000

# 定义启动命令
CMD ["python", "app.py"]