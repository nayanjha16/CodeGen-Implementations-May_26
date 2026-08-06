// DesignPatternsSolid | kind=solid | label=lsp | domain=discount | tier=errors
package org.example.patterns;

// LSP: subtypes usable wherever base discount shape is expected
abstract class DiscountShape {
    public abstract int area();
}

class DiscountRectangle extends DiscountShape {
    protected int w, h;
    public DiscountRectangle(int w, int h) { this.w = w; this.h = h; }
    public int area() { return w * h; }
}

class DiscountSquare extends DiscountShape {
    private final int side;
    public DiscountSquare(int side) { this.side = side; }
    public int area() { return side * side; }
}

public class DiscountLspUtil {
    public static int total(DiscountShape[] shapes) {
        int t = 0;
        for (DiscountShape sh : shapes) t += sh.area();
        return t;
    }
}
