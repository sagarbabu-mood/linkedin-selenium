ARG PORT=443
FROM selenium/standalone-chrome:latest
RUN apt-get install python3 -y
RUN echo $(python3 -m site --user-base)
COPY requirements.txt .
ENV PATH /home/root/.local/bin:${PATH}
RUN apt-get update && apt-get install -y python3-pip && \
    python3 -m pip install --upgrade pip && \
    pip install -r requirements.txt
COPY . .
CMD uvicorn back:app --host 0.0.0.0 --port ${PORT}