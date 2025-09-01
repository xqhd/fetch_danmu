FROM python:3.13

### for huggingface spaces
RUN useradd -m -u 1000 user

WORKDIR /app

# 先复制 requirements.txt 以利用 Docker 缓存
COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# 复制应用程序代码
COPY --chown=user . .

# 切换到非 root 用户
USER user
ENV PATH="/home/user/.local/bin:$PATH"

EXPOSE 8080

CMD ["python", "app.py"]
