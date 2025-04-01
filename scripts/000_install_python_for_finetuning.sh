#! /bin/sh

apt-get update
apt-get install -y software-properties-common
add-apt-repository ppa:deadsnakes/ppa -y

apt-get update
apt-get install -y python3.11 python3.11-venv
python3.11 -m ensurepip --upgrade

pip install torch
pip install unsloth
pip install xformers trl peft accelerate bitsandbytes huggingface_hub[cli]
pip install pandas matplotlib
pip install jupyter