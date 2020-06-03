# Build an image that can do training and inference in SageMaker
# This is a Python 3.7.3 image with pyenv that uses the nginx, gunicorn, flask stack
# for serving inferences in a stable way.
FROM python:3.7

RUN apt-get -y update && apt-get install -y --no-install-recommends git wget nginx ca-certificates && \
    mkdir -p /opt/program && \
    rm -rf /var/lib/apt/lists/*
ADD requirements.txt ./
RUN pip3 install --no-cache --upgrade pip & pip3 install -r ./requirements.txt
RUN python -c "import nltk; nltk.download('punkt'); nltk.download('wordnet'); nltk.download('stopwords')"

# Set some environment variables. PYTHONUNBUFFERED keeps Python from buffering our standard
# output stream, which means that logs can be delivered to the user quickly. PYTHONDONTWRITEBYTECODE
# keeps Python from writing the .pyc files which are unnecessary in this case. We also update
# PATH so that the train and serve programs are found when the container is invoked.
ENV PYTHONUNBUFFERED=TRUE
ENV PYTHONDONTWRITEBYTECODE=TRUE
ENV PATH="/opt/program:${PATH}"

# Set up the program in the image
COPY randomforest /opt/program
WORKDIR /opt/program

CMD ["/bin/bash"]

