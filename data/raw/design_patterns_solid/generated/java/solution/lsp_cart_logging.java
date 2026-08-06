// DesignPatternsSolid | kind=solid | label=lsp | domain=cart | tier=logging
package org.example.patterns;

// LSP: subtypes usable wherever base cart shape is expected
abstract class CartShape {
    public abstract int area();
}

class CartRectangle extends CartShape {
    protected int w, h;
    public CartRectangle(int w, int h) { this.w = w; this.h = h; }
    public int area() { return w * h; }
}

class CartSquare extends CartShape {
    private final int side;
    public CartSquare(int side) { this.side = side; }
    public int area() { return side * side; }
}

public class CartLspUtil {
    public static int total(CartShape[] shapes) {
        int t = 0;
        for (CartShape sh : shapes) t += sh.area();
        return t;
    }
}
