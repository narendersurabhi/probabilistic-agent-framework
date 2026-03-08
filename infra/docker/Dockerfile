FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "experiments/run_benchmark.py", "--config", "config/benchmark_config.yaml", "--output-dir", "artifacts"]
