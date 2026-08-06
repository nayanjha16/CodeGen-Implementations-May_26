// DesignPatternsSolid | kind=solid | label=lsp | domain=metrics | tier=errors
package org.example.patterns;

// LSP: subtypes usable wherever base metrics shape is expected
abstract class MetricsShape {
    public abstract int area();
}

class MetricsRectangle extends MetricsShape {
    protected int w, h;
    public MetricsRectangle(int w, int h) { this.w = w; this.h = h; }
    public int area() { return w * h; }
}

class MetricsSquare extends MetricsShape {
    private final int side;
    public MetricsSquare(int side) { this.side = side; }
    public int area() { return side * side; }
}

public class MetricsLspUtil {
    public static int total(MetricsShape[] shapes) {
        int t = 0;
        for (MetricsShape sh : shapes) t += sh.area();
        return t;
    }
}
