// DesignPatternsSolid | kind=solid | label=lsp | domain=report | tier=minimal
package org.example.patterns;

// LSP: subtypes usable wherever base report shape is expected
abstract class ReportShape {
    public abstract int area();
}

class ReportRectangle extends ReportShape {
    protected int w, h;
    public ReportRectangle(int w, int h) { this.w = w; this.h = h; }
    public int area() { return w * h; }
}

class ReportSquare extends ReportShape {
    private final int side;
    public ReportSquare(int side) { this.side = side; }
    public int area() { return side * side; }
}

public class ReportLspUtil {
    public static int total(ReportShape[] shapes) {
        int t = 0;
        for (ReportShape sh : shapes) t += sh.area();
        return t;
    }
}
