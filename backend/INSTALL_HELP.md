# Alternative Installation Methods for Trust Issues Backend

## If you're getting Rust/compilation errors with pip install

### Method 1: Install packages individually (Recommended)

```bash
pip install --upgrade pip
pip install fastapi
pip install "uvicorn[standard]"
pip install pydantic
pip install pydantic-settings
pip install python-dotenv
pip install requests
pip install google-generativeai
```

### Method 2: Use conda (if you have Anaconda/Miniconda)

```bash
conda create -n trustissues python=3.11
conda activate trustissues
pip install -r requirements.txt
```

### Method 3: Downgrade Python to 3.11 (Most Stable)

Python 3.14 is very new and some packages don't have pre-built wheels yet.

1. Download Python 3.11 from: https://www.python.org/downloads/
2. Install it
3. Use it for this project:
   ```bash
   py -3.11 -m pip install -r requirements.txt
   py -3.11 -m uvicorn app.main:app --reload
   ```

### Method 4: Install Microsoft Visual C++ Build Tools

If you want to keep Python 3.14, you need to install build tools to compile packages:

1. Download: https://visualstudio.microsoft.com/visual-cpp-build-tools/
2. Install "Desktop development with C++"
3. Restart terminal
4. Try: `pip install -r requirements.txt`

### Method 5: Use pre-built wheels (Quick Fix)

```bash
pip install --upgrade pip wheel setuptools
pip install --only-binary=:all: pydantic pydantic-core
pip install -r requirements.txt
```

## Verification

After installation, verify it works:

```bash
python test_setup.py
```

Should show all checks passing!

## Quick Test

```bash
python -c "import fastapi; import google.generativeai; print('✓ All imports working!')"
```

If you see "✓ All imports working!" you're good to go!
