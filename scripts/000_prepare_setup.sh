#! /bin/sh

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    echo "Activating virtual environment..."
    # shellcheck disable=SC2039
    source .venv/bin/activate
else
    echo "Creating python virtual environment"
    python -m venv .venv
    echo "Activating virtual environment..."
    # shellcheck disable=SC2039
    source .venv/bin/activate
fi

# Install dependencies
pip install uv
uv pip install -r requirements.txt

echo "DO NOT FORGET to 'source .env' if needed."