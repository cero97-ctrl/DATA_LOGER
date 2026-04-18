FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# Instalar dependencias base y PPA de KiCad 8.0 (Migración validada en ADN)
# Se agregan herramientas de compilación para C y prerrequisitos de ESP-IDF
RUN apt-get update && apt-get install -y \
    software-properties-common \
    python3 \
    python3-pip \
    python3-venv \
    git \
    wget \
    flex \
    bison \
    gperf \
    build-essential \
    cmake \
    ninja-build \
    ccache \
    libffi-dev \
    libssl-dev \
    dfu-util \
    libusb-1.0-0 \
    && add-apt-repository ppa:kicad/kicad-8.0-releases \
    && apt-get update \
    && apt-get install --install-recommends -y kicad \
    && apt-get install -y pcb2gcode \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Instalación optimizada de ESP-IDF para ESP32-S3
ENV IDF_PATH=/opt/esp-idf
ENV IDF_TOOLS_PATH=/opt/espressif

RUN git clone --recursive --depth 1 --shallow-submodules https://github.com/espressif/esp-idf.git $IDF_PATH \
    && $IDF_PATH/install.sh esp32s3 \
    && rm -rf $IDF_PATH/.git \
    && rm -rf $IDF_TOOLS_PATH/dist

# Alias para activar el entorno de ESP-IDF
RUN echo "source $IDF_PATH/export.sh > /dev/null 2>&1" >> /etc/bash.bashrc

# Configurar entorno Python para que reconozca la API nativa pcbnew
ENV PYTHONPATH="/usr/lib/python3/dist-packages:${PYTHONPATH}"

WORKDIR /home/kicad/project

COPY requirements.txt /tmp/requirements.txt
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt

CMD ["/bin/bash"]