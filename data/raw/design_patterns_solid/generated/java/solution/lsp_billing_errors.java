// DesignPatternsSolid | kind=solid | label=lsp | domain=billing | tier=errors
package org.example.patterns;

// LSP: subtypes usable wherever base billing shape is expected
abstract class BillingShape {
    public abstract int area();
}

class BillingRectangle extends BillingShape {
    protected int w, h;
    public BillingRectangle(int w, int h) { this.w = w; this.h = h; }
    public int area() { return w * h; }
}

class BillingSquare extends BillingShape {
    private final int side;
    public BillingSquare(int side) { this.side = side; }
    public int area() { return side * side; }
}

public class BillingLspUtil {
    public static int total(BillingShape[] shapes) {
        int t = 0;
        for (BillingShape sh : shapes) t += sh.area();
        return t;
    }
}
