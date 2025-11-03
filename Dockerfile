#CREDITS TO @CyberTGX

FROM python:3.10

RUN apt update && apt upgrade -y && apt install -y git

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

WORKDIR /app
COPY . .

CMD ["python3", "-m", "mfinder"]
