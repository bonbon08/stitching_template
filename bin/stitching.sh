#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "$(readlink -f "$0")")" && pwd)"

check_system() {
    python3 -c "import trimesh, shapely, numpy, PIL, matplotlib" 2>/dev/null
}

if check_system; then
    exec python3 "${SCRIPT_DIR}/main.py" "$@"
fi

VENV_DIR="${SCRIPT_DIR}/.venv"
if [ ! -f "$VENV_DIR/bin/python" ]; then
    echo "Erstelle virtuelle Umgebung..."
    python3 -m venv "$VENV_DIR"
    "$VENV_DIR/bin/pip" install --quiet mapbox-earcut manifold3d trimesh shapely numpy pillow matplotlib 2>&1
fi

exec "$VENV_DIR/bin/python" "${SCRIPT_DIR}/main.py" "$@"