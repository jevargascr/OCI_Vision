#!/bin/bash

# Actualizar e instalar herramientas necesarias
sudo dnf install git python38-pip -y
sudo dnf install -y gcc python3-devel
sudo pip3 install --upgrade pip setuptools wheel
pip3 install cython
pip3 install oci streamlit pillow pyarrow

# Instalar OCI CLI
sudo dnf -y install oraclelinux-developer-release-el8
sudo dnf install python36-oci-cli
oci --version


# Abrir Firewall
sudo firewall-cmd --permanent --add-port=8501/tcp
sudo firewall-cmd --reload