# setup_env.ps1 – One command environment setup for Horror Oracle

# 1. Use Python 3.11 to create the environment
$pythonPath = "C:\Program Files\WindowsApps\PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0\python.exe"

& $pythonPath -m venv C:\31000\horror_env

# 2. Activate environment
C:\31000\horror_env\Scripts\activate

# 3. Install all required packages
pip install --upgrade pip
pip install "numpy==1.26.4" "langchain==0.0.340" "langchain-openai==0.0.8" "chromadb==0.4.14" "openai==1.3.5" tiktoken

# 4. Lock environment for reuse
pip freeze > C:\31000\requirements.txt
