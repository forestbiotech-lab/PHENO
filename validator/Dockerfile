from python:3

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt


COPY webserver.py .
COPY miappe_validator.py . 
COPY validationstructure.json

LABEL version="1.0"

CMD ["python", "webserver.py"]

# docker build -t ontobrapi/validator
# docker run -it --rm --mount type=bind,source="$(pwd)"/../ontoBrAPI-node-docker/uploads,target=/usr/src/app/external ontobrapi/validator:latest python miappe_validator.py external/dados.xlsx

