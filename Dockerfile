# start by pulling the python image
FROM python:3.9-slim

# Set environment variables
ENV PYTHON_HOME /usr/local/bin/python
ENV PATH $PYTHON_HOME:$PATH

# switch working directory
WORKDIR /app

# copy every content from the local file to the image
COPY . /app

# install the dependencies and packages in the requirements file
RUN python3.9 -m pip install --no-cache-dir -r requirements.txt

RUN python3.9 -m spacy download en_core_web_sm

RUN python3.9 -m nltk.downloader punkt && python3.9 -m nltk.downloader wordnet

# configure the container to run in an executed manner
ENTRYPOINT [ "python" ]

CMD ["view.py" ]
