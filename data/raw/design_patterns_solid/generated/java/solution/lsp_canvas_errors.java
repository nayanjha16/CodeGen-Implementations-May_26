// DesignPatternsSolid | kind=solid | label=lsp | domain=canvas | tier=errors
package org.example.patterns;

// LSP: subtypes usable wherever base canvas shape is expected
abstract class CanvasShape {
    public abstract int area();
}

class CanvasRectangle extends CanvasShape {
    protected int w, h;
    public CanvasRectangle(int w, int h) { this.w = w; this.h = h; }
    public int area() { return w * h; }
}

class CanvasSquare extends CanvasShape {
    private final int side;
    public CanvasSquare(int side) { this.side = side; }
    public int area() { return side * side; }
}

public class CanvasLspUtil {
    public static int total(CanvasShape[] shapes) {
        int t = 0;
        for (CanvasShape sh : shapes) t += sh.area();
        return t;
    }
}
