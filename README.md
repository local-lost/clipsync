# ✂️ ClipSync

**ClipSync** is a lightweight, python-based cross-platform clipboard synchronization tool that allows multiple devices to share clipboard contents seamlessly over a network.

---

## 💡 Motivation

As a cyber-threat researcher, I often need to synchronize the clipboards of multiple machines during investigations and research.  
After struggling with overly complex and bloated solutions for such a simple task, I decided to build my own lightweight, no-fuss tool — **ClipSync**.

---

## 🚀 Features

- 🔄 Real-time clipboard syncing across devices.
- 🔦 Client/Server architecture inspired from [clipshare](https://github.com/reu/clipshare).
- ❌ Currently only supports text (Image and file support coming soon).
- 📋 Multi-device support: all connected devices share virtually share a common clipboard.
- 💻 Simple UI: Clean terminal interface implemented using [Textual](https://github.com/Textualize/textual).
- 🐍 Minimal dependencies: `pyperclip`, `textual`.

---

## 📦 Installation

### 📌 Requirements

- Python 3.7+
- `pip`
- `python-venv`

- NOTE: `pyperclip` on linux-based devices requires `xclip` to run

```bash
sudo apt-get install xclip
```

### 🛠️ Build from source

> It is recommended to install clipsync inside a virtual environment to not break any dependencies on your machine and not having to make any changes to your PATH environment variable.

```bash
python -m venv .venv
source .venv/bin/activate # or .\venv\Scripts\activate on Windows
git clone https://github.com/lokallost/clipsync.git
cd clipsync
python -m pip install .
```
---

## 👥 Usage

Run from the terminal using the `clipsync` command.

### Start the Server

```bash
clipsync server
```

Starts the sync server on default port `65432`.

### Start a Client

```bash
clipsync client <server_ip>
```

Once the client is connected to the server, the clipboard of the client is synced to the server.

---

## 🧪 Development Setup
> Contributions to the clipsync project are always welcome

```bash
git clone https://github.com/lokallost/clipsync.git
cd clipsync
python -m venv venv
source venv/bin/activate  # or .\venv\Scripts\activate on Windows
pip install -e .
```

---

## 📚 Dependencies

- [pyperclip](https://pypi.org/project/pyperclip/)
- [textual](https://pypi.org/project/textual/)

---

## ⚠️ Notes

- Ensure all devices are on the same network..
- No authentication or encryption is included (yet).

---

## 📝 License

This project is licensed under the [MIT License](LICENSE).

