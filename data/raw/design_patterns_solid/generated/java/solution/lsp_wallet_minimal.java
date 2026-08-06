// DesignPatternsSolid | kind=solid | label=lsp | domain=wallet | tier=minimal
package org.example.patterns;

// LSP: subtypes usable wherever base wallet shape is expected
abstract class WalletShape {
    public abstract int area();
}

class WalletRectangle extends WalletShape {
    protected int w, h;
    public WalletRectangle(int w, int h) { this.w = w; this.h = h; }
    public int area() { return w * h; }
}

class WalletSquare extends WalletShape {
    private final int side;
    public WalletSquare(int side) { this.side = side; }
    public int area() { return side * side; }
}

public class WalletLspUtil {
    public static int total(WalletShape[] shapes) {
        int t = 0;
        for (WalletShape sh : shapes) t += sh.area();
        return t;
    }
}
