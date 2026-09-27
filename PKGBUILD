# Maintainer: Stitch Template
pkgname=stitching-template
pkgver=1.0.0
pkgrel=1
pkgdesc="Generate 3D stitch canvas STL from images with live 3D preview"
arch=(any)
url="https://github.com/stitching-template"
license=(MIT)
depends=(python python-pillow python-numpy python-trimesh python-shapely python-manifold3d python-matplotlib)
optdepends=()
source=(src/main.py bin/stitching.sh stitching-template.desktop assets/kirby.png)
sha256sums=(SKIP SKIP SKIP SKIP)
install=$pkgname.install

package() {
    install -dm755 "$pkgdir/opt/$pkgname"
    install -Dm755 "$srcdir/bin/stitching.sh" "$pkgdir/opt/$pkgname/stitching.sh"
    install -Dm644 "$srcdir/src/main.py" "$pkgdir/opt/$pkgname/main.py"
    install -Dm644 "$srcdir/assets/kirby.png" "$pkgdir/opt/$pkgname/kirby.png"
    install -Dm644 "$srcdir/stitching-template.desktop" "$pkgdir/usr/share/applications/stitching-template.desktop"
    install -Dm644 "$srcdir/assets/kirby.png" "$pkgdir/usr/share/pixmaps/stitching-template.png"
    install -dm755 "$pkgdir/usr/bin"
    ln -sf "/opt/$pkgname/stitching.sh" "$pkgdir/usr/bin/stitching-template"
}