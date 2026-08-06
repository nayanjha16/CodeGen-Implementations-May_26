// DesignPatternsSolid | kind=solid | label=lsp | domain=shipping | tier=errors
package org.example.patterns;

// LSP: subtypes usable wherever base shipping shape is expected
abstract class ShippingShape {
    public abstract int area();
}

class ShippingRectangle extends ShippingShape {
    protected int w, h;
    public ShippingRectangle(int w, int h) { this.w = w; this.h = h; }
    public int area() { return w * h; }
}

class ShippingSquare extends ShippingShape {
    private final int side;
    public ShippingSquare(int side) { this.side = side; }
    public int area() { return side * side; }
}

public class ShippingLspUtil {
    public static int total(ShippingShape[] shapes) {
        int t = 0;
        for (ShippingShape sh : shapes) t += sh.area();
        return t;
    }
}
