# Maintainer: Stitch Template
pkgname=stitching-template
pkgver=1.0.0
pkgrel=1
pkgdesc="Generate 3D stitch canvas STL from images with live 3D preview"
arch=(any)
url="https://github.com/stitching-template"
license=(MIT)
depends=()
optdepends=()
source=("stitching-template-bin" "kirby.png-asset" "stitching-template.desktop")
sha256sums=(SKIP SKIP SKIP)
install=$pkgname.install

package() {
    install -dm755 "$pkgdir/opt/$pkgname"
    install -Dm755 "$srcdir/stitching-template-bin" "$pkgdir/opt/$pkgname/stitching-template"
    install -Dm644 "$srcdir/kirby.png-asset" "$pkgdir/opt/$pkgname/kirby.png"
    install -Dm644 "$srcdir/stitching-template.desktop" "$pkgdir/usr/share/applications/stitching-template.desktop"
    install -Dm644 "$srcdir/kirby.png-asset" "$pkgdir/usr/share/pixmaps/stitching-template.png"
    install -dm755 "$pkgdir/usr/bin"
    ln -sf "/opt/$pkgname/stitching-template" "$pkgdir/usr/bin/stitching-template"
}