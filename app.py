from __future__ import annotations
import os
import sys
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

    # State
    data_var = tk.StringVar()
    outfmt_var = tk.StringVar(value="png")
    err_var = tk.StringVar(value="M")
    svg_method_var = tk.StringVar(value="path")
    box_size_var = tk.IntVar(value=10)
    border_var = tk.IntVar(value=4)
    outpath_var = tk.StringVar(value=os.path.join(os.getcwd(), "qr_output.png"))

    # Layout
    frm = ttk.Frame(app, padding=12)
    frm.pack(fill=tk.BOTH, expand=True)

    ttk.Label(frm, text="Data / URL to encode:").grid(row=0, column=0, sticky="w")
    txt = tk.Text(frm, height=6, wrap="word")
    txt.grid(row=1, column=0, columnspan=3, sticky="nsew", pady=(4, 10))
    frm.rowconfigure(1, weight=1)
    frm.columnconfigure(1, weight=1)

    # Options
    optf = ttk.LabelFrame(frm, text="Options")
    optf.grid(row=2, column=0, columnspan=3, sticky="ew", pady=6)

    ttk.Label(optf, text="Format:").grid(row=0, column=0, sticky="w", padx=(8, 4), pady=4)
    ttk.Radiobutton(optf, text="PNG", variable=outfmt_var, value="png").grid(row=0, column=1, sticky="w")
    ttk.Radiobutton(optf, text="SVG", variable=outfmt_var, value="svg").grid(row=0, column=2, sticky="w")

    ttk.Label(optf, text="Error level:").grid(row=0, column=3, sticky="e", padx=(16, 4))
    ttk.Combobox(optf, textvariable=err_var, values=["L", "M", "Q", "H"], width=4, state="readonly").grid(row=0, column=4, sticky="w")

    ttk.Label(optf, text="Box size:").grid(row=1, column=0, sticky="e", padx=(8, 4))
    ttk.Spinbox(optf, from_=1, to=50, textvariable=box_size_var, width=6).grid(row=1, column=1, sticky="w")

    ttk.Label(optf, text="Border:").grid(row=1, column=2, sticky="e", padx=(8, 4))
    ttk.Spinbox(optf, from_=0, to=20, textvariable=border_var, width=6).grid(row=1, column=3, sticky="w")

    ttk.Label(optf, text="SVG method:").grid(row=1, column=4, sticky="e", padx=(16, 4))
    ttk.Combobox(optf, textvariable=svg_method_var, values=["path", "basic", "fragment"], width=10, state="readonly").grid(row=1, column=5, sticky="w")

    # Output
    outfrm = ttk.Frame(frm)
    outfrm.grid(row=3, column=0, columnspan=3, sticky="ew", pady=6)
    ttk.Label(outfrm, text="Save as:").pack(side=tk.LEFT)
    out_entry = ttk.Entry(outfrm, textvariable=outpath_var)
    out_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=6)

    def browse():
        fmt = outfmt_var.get()
        defext = ".png" if fmt == "png" else ".svg"
        filetypes = [("PNG Image", "*.png")] if fmt == "png" else [("SVG Image", "*.svg")]
        path = filedialog.asksaveasfilename(defaultextension=defext, filetypes=filetypes)
        if path:
            outpath_var.set(path)

    ttk.Button(outfrm, text="Browse…", command=browse).pack(side=tk.LEFT)

    # Preview (PNG only)
    preview_lbl = ttk.Label(frm, text="(PNG preview appears here after Generate)")
    preview_lbl.grid(row=4, column=0, columnspan=3, sticky="ew", pady=(8, 0))

    def generate():
        data = txt.get("1.0", "end").strip()
        if not data:
            messagebox.showerror("Error", "Please enter data/URL to encode.")
            return

        try:
            gen = QRCodeGenerator(error_level=err_var.get(), box_size=box_size_var.get(), border=border_var.get())
            fmt: OutFormat = outfmt_var.get()  # type: ignore
            if fmt == "png":
                if not _PIL_AVAILABLE:
                    messagebox.showerror("Dependency missing", "Pillow is required for PNG. Install with:\n\npip install pillow")
                    return
                img = gen.make_png(data)
            else:
                img = gen.make_svg(data, method=svg_method_var.get())  # type: ignore

            out_path = outpath_var.get()
            # Enforce extension based on chosen format
            base, ext = os.path.splitext(out_path)
            if fmt == "png" and ext.lower() != ".png":
                out_path = base + ".png"
                outpath_var.set(out_path)
            if fmt == "svg" and ext.lower() != ".svg":
                out_path = base + ".svg"
                outpath_var.set(out_path)

            saved = gen.save(img, out_path)

            # PNG preview
            if fmt == "png":
                from PIL import ImageTk  # lazy import
                tk_img = ImageTk.PhotoImage(file=saved)
                preview_lbl.configure(image=tk_img, text="")
                preview_lbl.image = tk_img
            else:
                preview_lbl.configure(text="SVG saved. Open it in your browser/vector app for preview.", image="")
                preview_lbl.image = None

            messagebox.showinfo("Success", f"QR saved to:\n{saved}")
        except Exception as e:
            messagebox.showerror("Generation failed", str(e))

    btnfrm = ttk.Frame(frm)
    btnfrm.grid(row=5, column=0, columnspan=3, pady=10)
    ttk.Button(btnfrm, text="Generate", command=generate).pack()

    app.mainloop()


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
    # New flags
    p.add_argument("--version", action="version", version="QR Tool v1.0.0")
    p.add_argument("--quiet", action="store_true", help="Suppress console output")
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

    if not args.quiet:
        print(f"Saved: {saved}")


if __name__ == "__main__":
    main()
