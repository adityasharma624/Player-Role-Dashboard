# How to Run the Player Role Dashboard

## ⚠️ Important: Use Streamlit Command

**DO NOT** run `python app.py` directly. Streamlit apps must be run with the `streamlit run` command.

## Quick Start

### Option 1: Using the run script (Easiest)
```bash
./run.sh
```

### Option 2: Manual command
```bash
# Activate virtual environment
source venv/bin/activate

# Run Streamlit
streamlit run app.py
```

### Option 3: One-liner
```bash
source venv/bin/activate && streamlit run app.py
```

## What to Expect

After running the command, you should see:
```
You can now view your Streamlit app in your browser.

Local URL: http://localhost:8501
Network URL: http://192.168.x.x:8501
```

The app will automatically open in your browser.

## Troubleshooting

### If you see warnings about "missing ScriptRunContext"
- This means you're running `python app.py` instead of `streamlit run app.py`
- **Solution**: Use `streamlit run app.py` instead

### If you see "module not found" errors
- Make sure the virtual environment is activated (you should see `(venv)` in your terminal)
- Run: `source venv/bin/activate`
- Then run: `streamlit run app.py`

### If the browser doesn't open automatically
- Copy the Local URL from the terminal output
- Paste it into your browser manually

## Stopping the App

Press `Ctrl+C` in the terminal to stop the Streamlit server.

