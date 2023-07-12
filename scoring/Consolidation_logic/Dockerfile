# Base & applications
FROM python:3.8.13
RUN apt-get --allow-releaseinfo-change update
RUN apt-get update && apt-get install -y libgomp1 libglib2.0-0 libsm6 libxrender1 libxext6 libgl1-mesa-glx vim ffmpeg

# Installs mlaaslib which is required for NW3.
ARG PIP_INDEX_URL
RUN pip install --index-url ${PIP_INDEX_URL} mlaaslib

RUN mkdir -p /home/ubuntu/mad/

# Python packages
ARG MODULE_NAME
COPY ./scoring/${MODULE_NAME}/requirements.txt /home/ubuntu/mad/requirements.txt
RUN pip install -r /home/ubuntu/mad/requirements.txt

COPY ./ /home/ubuntu/mad/lead_scoring/

# Check what the container contains 
RUN ls /home/ubuntu/mad/lead_scoring/scoring/${MODULE_NAME}/

# setuptools
RUN python /home/ubuntu/mad/lead_scoring/setup.py install

RUN ln -s /home/ubuntu/mad/lead_scoring/scoring/${MODULE_NAME}/main.py /home/ubuntu/mad/main.py
RUN ln -s /home/ubuntu/mad/lead_scoring/scoring/${MODULE_NAME}/side-car.py /home/ubuntu/mad/side-car.py

ENV PYTHONPATH="$PYTHONPATH:/home/ubuntu/mad/lead_scoring/"

ENTRYPOINT ["python", "/home/ubuntu/mad/side-car.py"]


