import numpy as np
from PIL import Image
import trimesh
from shapely.geometry import box, MultiPolygon
from shapely.ops import unary_union

def create_perfect_stitch_canvas(
    image_path: str,
    output_stl_path: str,
    pixel_size: float = 4.0,       # Rastergröße pro Pixel (mm)
    hole_radius: float = 0.75,     # Radius der Löcher (1.5mm Durchmesser)
    thickness: float = 1.6,        # Canvas-Stärke (mm)
    rim_height: float = 2.0,       # Höhe des Wand-Randes über dem Canvas (mm)
    rim_width: float = 3         # Wandstärke der Außenumrandung (mm)
):
    print(f"Lade Bild: {image_path}...")
    img = Image.open(image_path).convert("RGBA")
    arr = np.array(img)
    
    alpha = arr[:, :, 3]
    mask = alpha > 20
    
    height_px, width_px = mask.shape
    print(f"Bildgröße: {width_px}x{height_px} Pixel")

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
    print("Berechne Nahtlose 2D-Silhouette...")
    base_shape = unary_union(pixel_polygons)
    outer_shape = base_shape.buffer(rim_width, join_style=2)
    rim_shape = outer_shape.difference(base_shape)
    print("Extrudiere 3D-Geometrie...")
    base_mesh = trimesh.creation.extrude_polygon(base_shape, height=thickness)
    rim_mesh = trimesh.creation.extrude_polygon(rim_shape, height=thickness + rim_height)
    combined_body = trimesh.util.concatenate([base_mesh, rim_mesh])
    print(f"Erstelle {len(hole_nodes)} geteilte Eck-Löcher...")
    hole_cylinders = []
    total_h = thickness + rim_height + 4.0
    for hx, hy in hole_nodes:
        cyl = trimesh.creation.cylinder(radius=hole_radius, height=total_h)
        cyl.apply_translation([hx, hy, total_h / 2.0 - 1.0])
        hole_cylinders.append(cyl)
    holes_union = trimesh.util.concatenate(hole_cylinders)
    print("Stanze Löcher aus...")
    try:
        final_mesh = combined_body.difference(holes_union)
    except Exception:
        final_mesh = trimesh.boolean.difference([combined_body, holes_union])
    final_mesh.export(output_stl_path)
    print(f"Fertig! Perfektes Canvas gespeichert unter: {output_stl_path}")

if __name__ == "__main__":
    create_perfect_stitch_canvas(
        image_path="kirby.png",
        output_stl_path="kirby_canvas_v5.stl",
        pixel_size=4.0,       # Rastergröße eines Stick-Quadrats
        hole_radius=1.3,     # 1.5mm Lochdurchmesser
        thickness=1.6,        # Canvas-Bodendicke
        rim_height=2.0,       # 2mm Kante nach oben
        rim_width=3         # 1.2mm Wandstärke außen
    )