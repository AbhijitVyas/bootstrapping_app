# start by pulling the python image
FROM python:3.9-slim

# Set environment variables
ENV PYTHON_HOME /usr/local/bin/python
ENV PATH $PYTHON_HOME:$PATH

# switch working directory
WORKDIR /app

# copy every content from the local file to the image
COPY . /app

RUN apk --update --upgrade add --no-cache  gcc musl-dev jpeg-dev zlib-dev libffi-dev cairo-dev pango-dev gdk-pixbuf-dev

RUN python -m pip install --upgrade pip

# install the dependencies and packages in the requirements file
RUN python3.9 -m pip install --no-cache-dir -r requirements.txt

RUN python3.9 -m spacy download en_core_web_sm

# configure the container to run in an executed manner
ENTRYPOINT [ "python" ]

CMD ["view.py" ]
