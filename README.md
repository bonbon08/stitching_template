# Stitch Canvas Generator

Generate 3D stitch canvas STL files from images with live 3D preview.

## Features

- Load any image (PNG, JPG, BMP, TIFF)
- Real-time 2D image preview (scaled to fill)
- Generate 3D stitch canvas with holes
- Live 3D model preview before export
- Export as STL for 3D printing or CNC

## Parameters

- **Pixelgröße** — size of each stitch pixel in mm
- **Lochradius** — radius of drill holes
- **Canvas-Stärke** — bottom thickness
- **Randhöhe** — rim height above canvas
- **Randbreite** — outer rim thickness

## Usage

```bash
# With bundled venv (auto-creates on first run)
./stitching.sh

# Or directly with system Python
python3 main.py
```

## Installation

### Arch Linux (AUR)

```bash
git clone https://github.com/bonbon08/stitching_template.git
cd stitching-template
makepkg -si
```

This installs:
- App to `/opt/stitching-template/`
- Launcher script in `/usr/bin/stitching-template`
- Desktop entry and icon

## Manual

```bash
python3 -m venv .venv
.venv/bin/pip install mapbox-earcut manifold3d trimesh shapely numpy pillow matplotlib
.venv/bin/python src/main.py
```

## Dependencies

- Python 3.10+
- numpy, Pillow, trimesh, shapely, manifold3d, matplotlib
- Or: `mapbox-earcut` instead of `manifold3d`

## License

MIT