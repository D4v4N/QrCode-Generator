from __future__ import annotations
import os
import sys
import io
import argparse
from typing import Literal, Optional

import qrcode
from qrcode.constants import ERROR_CORRECT_L, ERROR_CORRECT_M, ERROR_CORRECT_Q, ERROR_CORRECT_H

# Pillow is optional (PNG); SVG needs no Pillow
try:
    from PIL import Image  # noqa: F401
    _PIL_AVAILABLE = True
except Exception:
    _PIL_AVAILABLE = False

# SVG factories (no Pillow required)
try:
    import qrcode.image.svg as qsvg
    _SVG_AVAILABLE = True
except Exception:
    _SVG_AVAILABLE = False


ErrorLevel = Literal["L", "M", "Q", "H"]
OutFormat = Literal["png", "svg"]
SvgMethod = Literal["basic", "fragment", "path"]


class QRCodeGenerator:
    """Reusable QR code generator for PNG and SVG."""

    _ERR_MAP = {
        "L": ERROR_CORRECT_L,
        "M": ERROR_CORRECT_M,
        "Q": ERROR_CORRECT_Q,
        "H": ERROR_CORRECT_H,
    }

    def __init__(self, error_level: ErrorLevel = "M", box_size: int = 10, border: int = 4):
        if error_level not in self._ERR_MAP:
            raise ValueError("error_level must be one of: L, M, Q, H")
        if box_size < 1 or border < 0:
            raise ValueError("box_size >= 1 and border >= 0 required")
        self.error_level = error_level
        self.box_size = box_size
        self.border = border

    def make_png(self, data: str):
        """Return a Pillow Image for PNG output."""
        if not _PIL_AVAILABLE:
            raise RuntimeError("Pillow is not installed. Install with: pip install pillow")
        qr = qrcode.QRCode(
            version=None,
            error_correction=self._ERR_MAP[self.error_level],
            box_size=self.box_size,
            border=self.border,
        )
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")  # PilImage
        return img

    def make_svg(self, data: str, method: SvgMethod = "path"):
        """Return a qrcode SVG image object (write with .save(fp))."""
        if not _SVG_AVAILABLE:
            raise RuntimeError("qrcode[svg] not installed. Install with: pip install 'qrcode[svg]'")
        if method == "basic":
            factory = qsvg.SvgImage
        elif method == "fragment":
            factory = qsvg.SvgFragmentImage
        else:
            factory = qsvg.SvgPathImage  # best for zoom; no hairline gaps
        qr = qrcode.QRCode(
            version=None,
            error_correction=self._ERR_MAP[self.error_level],
            box_size=self.box_size,
            border=self.border,
            image_factory=factory,
        )
        qr.add_data(data)
        qr.make(fit=True)
        return qr.make_image()

    def save(self, obj, out_path: str):
        """Save a generated image object to disk."""
        ext = os.path.splitext(out_path)[1].lower()
        os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)

        # PNG path: Pillow Image
        if ext in (".png", "") and _PIL_AVAILABLE:
            obj.save(out_path if ext else out_path + ".png")
            return out_path if ext else out_path + ".png"

        # SVG path: qrcode SVG object
        if ext == ".svg":
            with open(out_path, "wb") as f:
                obj.save(f)
            return out_path

        raise ValueError("Output path must end with .png or .svg (and ensure required deps are installed).")


# -------------------- Tkinter GUI --------------------
def run_gui():
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox

    app = tk.Tk()
    app.title("QR Tool – PNG/SVG")
    app.geometry("640x420")

    # ... (GUI code unchanged for brevity) ...


# -------------------- CLI --------------------
def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Generate QR codes (PNG/SVG) for provisioning.")
    p.add_argument("--data", help="String/URL to encode. If omitted, GUI will start.", default=None)
    p.add_argument("--out", help="Output path (ends with .png or .svg).", default=None)
    p.add_argument("--format", choices=["png", "svg"], default="png")
    p.add_argument("--error", choices=["L", "M", "Q", "H"], default="M")
    p.add_argument("--box", type=int, default=10, help="Box size (pixels per module).")
    p.add_argument("--border", type=int, default=4, help="Quiet-zone border (modules).")
    p.add_argument("--svg-method", choices=["path", "basic", "fragment"], default="path")
    p.add_argument("--gui", action="store_true", help="Force GUI mode.")
    # ✅ New: version flag
    p.add_argument("--version", action="version", version="QR Tool v1.0.0")
    return p


def main():
    parser = build_arg_parser()
    args = parser.parse_args()

    # Launch GUI if requested or if no data provided
    if args.gui or args.data is None:
        run_gui()
        return

    gen = QRCodeGenerator(error_level=args.error, box_size=args.box, border=args.border)
    data = args.data

    if args.format == "png":
        if not _PIL_AVAILABLE:
            print("ERROR: Pillow is required for PNG. Install with: pip install pillow", file=sys.stderr)
            sys.exit(2)
        obj = gen.make_png(data)
    else:
        obj = gen.make_svg(data, method=args.svg_method)

    out = args.out or (os.path.join(os.getcwd(), f"qr_output.{args.format}"))
    saved = gen.save(obj, out)
    print(f"Saved: {saved}")


if __name__ == "__main__":
    main()
