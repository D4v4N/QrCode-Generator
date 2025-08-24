# QR Code Generator

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

A simple, cross-platform **QR code generator** written in Python.  
Supports **PNG** (via Pillow) and **SVG** output with customizable error correction, box size, border, and rendering methods.  
Includes a **Tkinter GUI** for easy use and a **CLI** for automation or integration in provisioning workflows (e.g., SIP/VoIP account setup).

## About UDP Consulting  
This project is maintained by [UDP Consulting](https://udpconsulting.com), specialists in SEO consulting and VoIP development.  
---

## ✨ Features

- Generate **QR codes** as **PNG** or **SVG**
- Built-in **Tkinter GUI** (with live PNG preview)
- **CLI mode** for scripting and batch processing
- Adjustable:
  - Error correction level (**L, M, Q, H**)
  - Box size & border
  - SVG rendering method (**path**, **basic**, **fragment**)
- Cross-platform (Windows, macOS, Linux)

---

## 🚀 Installation

Clone the repository and install dependencies:

```bash
git clone https://github.com/D4v4N/QrCode-Generator.git
cd QrCode-Generator
pip install -r requirements.txt
