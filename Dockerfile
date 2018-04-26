FROM registry.datadrivendiscovery.org/jpl/docker_images/complete:ubuntu-artful-python36-devel-20180419-092215

# Pick up some TF dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libssl-dev \
        curl \
        git \
        libfreetype6-dev \
        libpng12-dev \
        libzmq3-dev \
        libjpeg-dev \
        libtiff-dev \
        zlib1g-dev \
        pkg-config \
        python3 \
        python3-dev \
        rsync \
        software-properties-common \
        unzip \
        python3-tk \
        apt-transport-https \
        tesseract-ocr \
        libtesseract-dev \
        libleptonica-dev 

RUN apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN curl -O https://bootstrap.pypa.io/get-pip.py && \
    python3 get-pip.py && \
    rm get-pip.py

RUN curl -O https://bootstrap.pypa.io/get-pip.py && \
    python3 get-pip.py && \
    rm get-pip.py

RUN pip3 --no-cache-dir install \
        setuptools \
        ipykernel \
        jupyter \
        matplotlib \
        numpy \
        scipy \
        sklearn \
        pandas \
        Pillow \
        keras \
        h5py \
        flask \
        requests \
        tesserocr \
        spacy \
        && \
    python3 -m ipykernel.kernelspec
    
# --- DO NOT EDIT OR DELETE BETWEEN THE LINES --- #
# These lines will be edited automatically by parameterized_docker_build.sh. #
# COPY _PIP_FILE_ /
# RUN pip --no-cache-dir install /_PIP_FILE_
# RUN rm -f /_PIP_FILE_

# Install TensorFlow GPU version.
RUN pip3 --no-cache-dir install \
    https://storage.googleapis.com/tensorflow/linux/cpu/tensorflow-1.2.1-cp35-cp35m-linux_x86_64.whl
# --- ~ DO NOT EDIT OR DELETE BETWEEN THE LINES --- #

RUN python3 -m spacy download en

COPY . /croc/

# For CUDA profiling, TensorFlow requires CUPTI.
ENV LD_LIBRARY_PATH /usr/local/cuda/extras/CUPTI/lib64:$LD_LIBRARY_PATH

WORKDIR ./croc

RUN mkdir target_imgs

ENV LC_ALL=C.UTF-8 \
    LANG=C.UTF-8

RUN echo $LC_ALL &&\
    echo $LANG

RUN chmod +x start_flask.sh &&\     
    sync

CMD ./start_flask.sh