FROM python:3.13-slim
WORKDIR /app
COPY pyproject.toml ./
COPY src/quantpilot ./src/quantpilot
RUN pip install --no-cache-dir .
USER 65534:65534
CMD ["python", "-m", "quantpilot.demo"]
