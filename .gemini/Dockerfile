FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# Instalar herramientas de compilación y dependencias base
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    cmake \
    make \
    git \
    python3 \
    python3-pip \
    curl \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Directorio de trabajo para las validaciones del Motor de Análisis
WORKDIR /sandbox

# Por defecto, iniciamos en bash para permitir la orquestación de comandos
CMD ["/bin/bash"]