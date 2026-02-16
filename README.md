# DictScope 🔭

**DictScope** is a lightweight, dependency-free tool to visualize Python dictionaries and JSON data in your browser in real-time. 

Perfect for debugging scripts, monitoring loops, and inspecting complex nested data structures without spamming your console.

## ✨ Features

- **Zero Dependencies**: Uses only Python standard library.
- **Real-time**: Updates automatically as your data changes.
- **Interactive**: Collapse and expand nested lists and dictionaries.
- **Network Ready**: View data from your phone or another laptop in the local network.
- **Dark Mode**: Easy on the eyes.

## 📦 Installation

### Via uv (Recommended)
```bash
uv add dictscope
```
or
```bash
uv add git+https://github.com/Zidrax/dictscope.git
```

### Via pip
```Bash
pip install dictscope
```

### 🚀 Usage

Just import render and pass any dictionary to it. DictScope will start a local server and open your browser automatically.
```Python
from dictscope import render
import time
import math
# 1. Prepare your data
data = {
    "status": "running",
    "metrics": {"cpu": 0, "memory": []},
    "config": {"debug": True}
}
# 2. Update it in a loop
for i in range(100):
    data["metrics"]["cpu"] = math.sin(i / 10)
    data["metrics"]["memory"].append(i)
    
    # 3. Render! (Browser updates automatically)
    render(data)
    
    time.sleep(0.1)
```

⏸ Controls

Pause/Resume: Click the button in the top right corner to freeze the data stream and inspect the current state.

Collapse/Expand: Click on the ▼ arrows to navigate deep JSON structures.