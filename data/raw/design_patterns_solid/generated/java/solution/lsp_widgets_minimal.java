// DesignPatternsSolid | kind=solid | label=lsp | domain=widgets | tier=minimal
package org.example.patterns;

// LSP: subtypes usable wherever base widgets shape is expected
abstract class WidgetsShape {
    public abstract int area();
}

class WidgetsRectangle extends WidgetsShape {
    protected int w, h;
    public WidgetsRectangle(int w, int h) { this.w = w; this.h = h; }
    public int area() { return w * h; }
}

class WidgetsSquare extends WidgetsShape {
    private final int side;
    public WidgetsSquare(int side) { this.side = side; }
    public int area() { return side * side; }
}

public class WidgetsLspUtil {
    public static int total(WidgetsShape[] shapes) {
        int t = 0;
        for (WidgetsShape sh : shapes) t += sh.area();
        return t;
    }
}
