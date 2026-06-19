FROM public.ecr.aws/docker/library/python:3.11-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

COPY agentcore-requirements.txt .

RUN pip install --no-cache-dir -r agentcore-requirements.txt

COPY app ./app
COPY agentcore_agent.py .

CMD ["python", "agentcore_agent.py"]