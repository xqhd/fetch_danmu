FROM python:3.13

### for huggingface spaces
RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH"


WORKDIR /app

COPY --chown=user . .

RUN pip install --no-cache-dir --upgrade -r requirements.txt


EXPOSE 8080

CMD ["python3", "-m", "robyn","app.py", "--fast", "--processes", "2", "--workers", "4", "--log-level=DEBUG"]
