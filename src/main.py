import sys
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import numpy as np
import trimesh
from shapely.geometry import box
from shapely.ops import unary_union
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


def check_dependencies():
    missing = []
    for mod in ["manifold3d", "trimesh", "shapely", "numpy", "PIL", "matplotlib"]:
        try:
            __import__(mod)
        except ImportError:
            missing.append(mod)
    if missing:
        return f"Fehlende Abhängigkeiten: {', '.join(missing)}\nInstalliere mit: sudo pacman -S {' '.join(missing)}"
    return None


def create_perfect_stitch_canvas(
    image_path: str,
    output_stl_path: str,
    pixel_size: float = 4.0,
    hole_radius: float = 0.75,
    thickness: float = 1.6,
    rim_height: float = 2.0,
    rim_width: float = 3,
    progress_cb=None,
):
    def cb(msg):
        if progress_cb:
            progress_cb(msg)
        print(msg)

    cb(f"Lade Bild: {image_path}...")
    img = Image.open(image_path).convert("RGBA")
    arr = np.array(img)

    alpha = arr[:, :, 3]
    mask = alpha > 20

    height_px, width_px = mask.shape
    cb(f"Bildgröße: {width_px}x{height_px} Pixel")

    if not np.any(mask):
        raise ValueError("Keine sichtbaren Pixel gefunden!")

    pixel_polygons = []
    hole_nodes = set()

    for y in range(height_px):
        for x in range(width_px):
            if mask[y, x]:
                x0 = x * pixel_size
                x1 = (x + 1) * pixel_size
                y0 = (height_px - 1 - y) * pixel_size
                y1 = (height_px - y) * pixel_size
                pixel_polygons.append(box(x0, y0, x1, y1))
                hole_nodes.add((round(x0, 4), round(y0, 4)))
                hole_nodes.add((round(x1, 4), round(y0, 4)))
                hole_nodes.add((round(x0, 4), round(y1, 4)))
                hole_nodes.add((round(x1, 4), round(y1, 4)))

    cb("Berechne nahtlose 2D-Silhouette...")
    base_shape = unary_union(pixel_polygons)
    outer_shape = base_shape.buffer(rim_width, join_style=2)
    rim_shape = outer_shape.difference(base_shape)

    cb("Extrudiere 3D-Geometrie...")
    base_mesh = trimesh.creation.extrude_polygon(base_shape, height=thickness, engine="manifold")
    rim_mesh = trimesh.creation.extrude_polygon(rim_shape, height=thickness + rim_height, engine="manifold")
    combined_body = trimesh.util.concatenate([base_mesh, rim_mesh])

    cb(f"Erstelle {len(hole_nodes)} geteilte Eck-Löcher...")
    hole_cylinders = []
    total_h = thickness + rim_height + 4.0
    for hx, hy in hole_nodes:
        cyl = trimesh.creation.cylinder(radius=hole_radius, height=total_h)
        cyl.apply_translation([hx, hy, total_h / 2.0 - 1.0])
        hole_cylinders.append(cyl)
    holes_union = trimesh.util.concatenate(hole_cylinders)

    cb("Stanze Löcher aus...")
    final_mesh = combined_body.difference(holes_union)
    final_mesh.export(output_stl_path)
    cb(f"Fertig! Canvas gespeichert unter: {output_stl_path}")
    return output_stl_path, final_mesh


def mesh_to_image(mesh, width=480, height=360):
    fig = plt.figure(figsize=(width / 100, height / 100), dpi=100)
    ax = fig.add_subplot(111, projection="3d")
    verts = mesh.vertices
    faces = mesh.faces
    ax.plot_trisurf(
        verts[:, 0], verts[:, 1], verts[:, 2],
        triangles=faces,
        cmap="coolwarm",
        edgecolor="none",
        alpha=0.9,
        linewidth=0,
        antialiased=True,
    )
    ax.set_axis_off()
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.set_zlabel("")
    ax.xaxis.pane.fill = False
    ax.yaxis.pane.fill = False
    ax.zaxis.pane.fill = False
    ax.xaxis.pane.set_edgecolor("none")
    ax.yaxis.pane.set_edgecolor("none")
    ax.zaxis.pane.set_edgecolor("none")
    ax.xaxis._axinfo["grid"]["color"] = (1, 1, 1, 0)
    ax.yaxis._axinfo["grid"]["color"] = (1, 1, 1, 0)
    ax.zaxis._axinfo["grid"]["color"] = (1, 1, 1, 0)
    ax.view_init(elev=25, azim=-60)
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1, wspace=0, hspace=0)
    fig.canvas.draw()
    buf = fig.canvas.buffer_rgba()
    im = Image.frombytes("RGBA", fig.canvas.get_width_height(), buf)
    im = im.resize((width, height), Image.LANCZOS)
    plt.close(fig)
    return im


class StitchApp:
    def __init__(self, root):
        self.root = root
        self.photo = None
        self.preview_image = None
        self.current_mesh = None

        root.title("Stitch Canvas Generator")
        root.geometry("1000x900")
        root.minsize(800, 700)

        dep_err = check_dependencies()
        if dep_err:
            messagebox.showerror("Fehlende Abhängigkeiten", dep_err)
            sys.exit(1)

        style = ttk.Style(root)
        style.theme_use("clam")
        style.configure("TFrame", background="#2d2d2d")
        style.configure("TLabel", background="#2d2d2d", foreground="#e0e0e0", font=("Segoe UI", 10))
        style.configure("Header.TLabel", background="#2d2d2d", foreground="#4fc3f7", font=("Segoe UI", 12, "bold"))
        style.configure("TButton", font=("Segoe UI", 10), padding=6)
        style.configure("Preview.TButton", font=("Segoe UI", 11, "bold"), padding=8)
        style.configure("Export.TButton", font=("Segoe UI", 11, "bold"), padding=8)
        style.configure("TSpinbox", font=("Segoe UI", 10))
        style.configure("TEntry", font=("Segoe UI", 10))
        style.configure("Status.TLabel", background="#1e1e1e", foreground="#66bb6a", font=("Segoe UI", 9))
        style.configure("Log.TFrame", background="#1e1e1e")

        main_frame = ttk.Frame(root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        top = ttk.Frame(main_frame)
        top.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        ttk.Label(top, text="Bildvorschau", style="Header.TLabel").pack(anchor=tk.W)
        self.image_canvas = tk.Canvas(top, bg="#1a1a2e", highlightthickness=1, highlightbackground="#444", height=200)
        self.image_canvas.pack(fill=tk.X, pady=(5, 0))

        ttk.Label(top, text="Bilddatei", style="Header.TLabel").pack(anchor=tk.W, pady=(10, 0))
        img_row = ttk.Frame(top)
        img_row.pack(fill=tk.X, pady=(5, 0))
        self.image_var = tk.StringVar(value="")
        ttk.Entry(img_row, textvariable=self.image_var, width=40).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(img_row, text="Browse", command=self.browse_image).pack(side=tk.RIGHT, padx=(5, 0))

        ttk.Label(top, text="Ausgabe STL", style="Header.TLabel").pack(anchor=tk.W, pady=(10, 0))
        out_row = ttk.Frame(top)
        out_row.pack(fill=tk.X)
        self.output_var = tk.StringVar(value="")
        ttk.Entry(out_row, textvariable=self.output_var, width=40).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(out_row, text="Browse", command=self.browse_output).pack(side=tk.RIGHT, padx=(5, 0))

        ttk.Separator(top, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)

        params = [
            ("Pixelgröße (mm)", "pixel_size_var", 0.5, 20.0, 0.5, 4.0),
            ("Lochradius (mm)", "hole_radius_var", 0.2, 5.0, 0.1, 0.75),
            ("Canvas-Stärke (mm)", "thickness_var", 0.5, 10.0, 0.1, 1.6),
            ("Randhöhe (mm)", "rim_height_var", 0.0, 10.0, 0.5, 2.0),
            ("Randbreite (mm)", "rim_width_var", 0.5, 15.0, 0.5, 3.0),
        ]
        self.spin_vars = {}
        for label, attr, fr, to, inc, default in params:
            row = ttk.Frame(top)
            row.pack(fill=tk.X, pady=2)
            ttk.Label(row, text=label, width=20).pack(side=tk.LEFT)
            var = tk.DoubleVar(value=default)
            self.spin_vars[attr] = var
            ttk.Spinbox(row, from_=fr, to=to, increment=inc, textvariable=var, width=8).pack(side=tk.RIGHT)

        ttk.Separator(top, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)

        btn_row = ttk.Frame(top)
        btn_row.pack(fill=tk.X)
        self.preview_btn = ttk.Button(btn_row, text="Vorschau", command=self.preview, style="Preview.TButton")
        self.preview_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 3))
        self.export_btn = ttk.Button(btn_row, text="Exportieren", command=self.export, style="Export.TButton")
        self.export_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(3, 0))

        self.status_var = tk.StringVar(value="Bereit.")
        ttk.Label(top, textvariable=self.status_var, style="Status.TLabel").pack(anchor=tk.W, pady=(10, 5))

        log_frame = ttk.Frame(top)
        log_frame.pack(fill=tk.X, pady=(5, 0))
        ttk.Label(log_frame, text="Log", style="Header.TLabel").pack(anchor=tk.W)
        self.log_text = tk.Text(log_frame, height=5, width=60, bg="#1e1e1e", fg="#66bb6a",
                                   insertbackground="#fff", font=("Consolas", 9), state=tk.DISABLED)
        self.log_text.pack(fill=tk.X, pady=(5, 0))

        bottom = ttk.Frame(main_frame)
        bottom.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, pady=(5, 0))

        ttk.Label(bottom, text="3D-Vorschau", style="Header.TLabel").pack(anchor=tk.W)
        self.preview_canvas = tk.Canvas(bottom, bg="#1a1a2e", highlightthickness=1, highlightbackground="#444")
        self.preview_canvas.pack(fill=tk.BOTH, expand=True, pady=(5, 0))

        self.image_var.trace_add("write", lambda *a: self.on_image_change())
        self.root.after(100, self.on_image_change)

    def browse_image(self):
        path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.tif *.tiff")])
        if path:
            self.image_var.set(path)

    def browse_output(self):
        path = filedialog.asksaveasfilename(defaultextension=".stl", filetypes=[("STL files", "*.stl")])
        if path:
            self.output_var.set(path)

    def log(self, msg):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, msg + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def on_image_change(self):
        path = self.image_var.get()
        if not path or not os.path.isfile(path):
            self.image_canvas.delete("all")
            self.image_canvas.create_text(200, 80, text="Kein Bild geladen", fill="#555", font=("Segoe UI", 14))
            self.preview_image = None
            return
        try:
            img = Image.open(path).convert("RGBA")
            self.preview_image = img
            self.status_var.set(f"Bild geladen: {os.path.basename(path)} ({img.size[0]}x{img.size[1]})")
            self.draw_image_preview()
        except Exception as e:
            self.log(f"Fehler beim Laden: {e}")
            self.status_var.set("Fehler beim Laden")

    def draw_image_preview(self):
        if self.preview_image is None:
            return
        cw = self.image_canvas.winfo_width()
        ch = self.image_canvas.winfo_height()
        if cw < 10 or ch < 10:
            self.root.after(50, self.draw_image_preview)
            return
        cw -= 2
        ch -= 2
        img = self.preview_image.copy()
        img.thumbnail((cw, ch), Image.LANCZOS)
        pw, ph = img.size
        ox = (cw - pw) // 2
        oy = (ch - ph) // 2
        self.photo = ImageTk.PhotoImage(img)
        self.image_canvas.delete("all")
        self.image_canvas.create_rectangle(0, 0, cw + 2, ch + 2, fill="#1a1a2e", outline="#444")
        self.image_canvas.create_image(ox, oy, anchor=tk.NW, image=self.photo)

    def preview(self):
        if not self.image_var.get() or not os.path.isfile(self.image_var.get()):
            messagebox.showwarning("Kein Bild", "Bitte zuerst ein Bild laden.")
            return
        self.preview_btn.config(state=tk.DISABLED)
        self.export_btn.config(state=tk.DISABLED)
        self.status_var.set("Vorschau wird generiert...")
        self.root.update()
        try:
            output_stl = "/tmp/_preview.stl"
            _, mesh = self._generate(output_stl)
            self.current_mesh = mesh
            self.status_var.set("Vorschau bereit.")
            self.log("Vorschau generiert.")
            self.root.after(0, self.show_3d_preview)
        except Exception as e:
            self.status_var.set("Fehler!")
            self.log(f"FEHLER: {e}")
            messagebox.showerror("Fehler", str(e))
        finally:
            self.preview_btn.config(state=tk.NORMAL)
            self.export_btn.config(state=tk.NORMAL)

    def _generate(self, output_stl_path):
        return create_perfect_stitch_canvas(
            image_path=self.image_var.get(),
            output_stl_path=output_stl_path,
            pixel_size=self.spin_vars["pixel_size_var"].get(),
            hole_radius=self.spin_vars["hole_radius_var"].get(),
            thickness=self.spin_vars["thickness_var"].get(),
            rim_height=self.spin_vars["rim_height_var"].get(),
            rim_width=self.spin_vars["rim_width_var"].get(),
            progress_cb=self.log,
        )

    def show_3d_preview(self):
        if self.current_mesh is None:
            return
        try:
            im = mesh_to_image(self.current_mesh, width=480, height=360)
            self.photo = ImageTk.PhotoImage(im)
            self.preview_canvas.delete("all")
            cw = self.preview_canvas.winfo_width() - 2
            ch = self.preview_canvas.winfo_height() - 2
            self.preview_canvas.create_rectangle(0, 0, cw + 2, ch + 2, fill="#1a1a2e", outline="#444")
            ox = (cw - im.width) // 2
            oy = (ch - im.height) // 2
            self.preview_canvas.create_image(ox, oy, anchor=tk.NW, image=self.photo)
        except Exception as e:
            self.log(f"Render-Fehler: {e}")

    def export(self):
        if self.current_mesh is None:
            messagebox.showwarning("Keine Vorschau", "Bitte zuerst eine Vorschau generieren.")
            return
        if not self.output_var.get():
            messagebox.showwarning("Kein Pfad", "Bitte einen Ausgabepfad wählen.")
            return
        self.export_btn.config(state=tk.DISABLED)
        self.status_var.set("Exportiere...")
        self.root.update()
        try:
            self.current_mesh.export(self.output_var.get())
            self.status_var.set("Exportiert!")
            self.log(f"Exportiert: {self.output_var.get()}")
            messagebox.showinfo("Erfolg", f"Canvas gespeichert unter:\n{self.output_var.get()}")
        except Exception as e:
            self.status_var.set("Fehler!")
            self.log(f"FEHLER: {e}")
            messagebox.showerror("Fehler", str(e))
        finally:
            self.export_btn.config(state=tk.NORMAL)


def main():
    root = tk.Tk()
    app = StitchApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()