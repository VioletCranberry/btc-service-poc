FROM python:3.9-slim as build

WORKDIR /usr/app

# Create a virtual environment
RUN python -m venv /usr/app/venv
ENV PATH="/usr/app/venv/bin:$PATH"

# Disable pip version check and python version warning
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PIP_NO_PYTHON_VERSION_WARNING=1

# Install dependencies
COPY ./requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

FROM python:3.9-slim as final

WORKDIR /usr/app

# Copy the application code and venv to the container
COPY --from=build /usr/app/venv ./venv
COPY app ./app
ENV PATH="/usr/app/venv/bin:$PATH"

# Prevent Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED=1

# Create a non-root user and group, change ownership
RUN groupadd -r appuser && \
  useradd -r -g appuser -u 1001 appuser && \
  chown -R appuser:appuser /usr/app
USER appuser

CMD ["python", "./app/main.py"]

