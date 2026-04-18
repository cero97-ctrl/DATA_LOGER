FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# Instalar dependencias base y PPA de KiCad 8.0 (Migración validada en ADN)
RUN apt-get update && apt-get install -y \
    software-properties-common \
    python3 \
    python3-pip \
    git \
    && add-apt-repository ppa:kicad/kicad-8.0-releases \
    && apt-get update \
    && apt-get install --install-recommends -y kicad \
    && apt-get install -y pcb2gcode \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Configurar entorno Python para que reconozca la API nativa pcbnew
ENV PYTHONPATH="/usr/lib/python3/dist-packages:${PYTHONPATH}"

WORKDIR /home/kicad/project

COPY requirements.txt /tmp/requirements.txt
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt

CMD ["/bin/bash"]