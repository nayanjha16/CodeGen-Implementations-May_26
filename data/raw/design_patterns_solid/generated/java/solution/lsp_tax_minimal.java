// DesignPatternsSolid | kind=solid | label=lsp | domain=tax | tier=minimal
package org.example.patterns;

// LSP: subtypes usable wherever base tax shape is expected
abstract class TaxShape {
    public abstract int area();
}

class TaxRectangle extends TaxShape {
    protected int w, h;
    public TaxRectangle(int w, int h) { this.w = w; this.h = h; }
    public int area() { return w * h; }
}

class TaxSquare extends TaxShape {
    private final int side;
    public TaxSquare(int side) { this.side = side; }
    public int area() { return side * side; }
}

public class TaxLspUtil {
    public static int total(TaxShape[] shapes) {
        int t = 0;
        for (TaxShape sh : shapes) t += sh.area();
        return t;
    }
}
