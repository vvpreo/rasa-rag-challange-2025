#! /bin/sh

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    echo "Activating virtual environment..."
    source .venv/bin/activate
else
    echo "Creating python virtual environment"
    python -m venv .venv
    echo "Activating virtual environment..."
    source .venv/bin/activate
fi

pip install uv
uv pip install -r requirements.txt
