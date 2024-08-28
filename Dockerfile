FROM ollama/ollama

WORKDIR /code

COPY ./requirements.txt ./

RUN apt-get update && apt-get install git -y && apt-get install curl -y

RUN curl -fsSL https://ollama.com/install.sh | sh

RUN apt list | grep python

RUN apt install -y python3 python3-pip

RUN pip install --no-cache-dir -r requirements.txt

COPY ./src ./src

CMD ["python", "/code/src/main.py"]
