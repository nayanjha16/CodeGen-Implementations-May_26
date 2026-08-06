// DesignPatternsSolid | kind=solid | label=lsp | domain=sensors | tier=logging
package org.example.patterns;

// LSP: subtypes usable wherever base sensors shape is expected
abstract class SensorsShape {
    public abstract int area();
}

class SensorsRectangle extends SensorsShape {
    protected int w, h;
    public SensorsRectangle(int w, int h) { this.w = w; this.h = h; }
    public int area() { return w * h; }
}

class SensorsSquare extends SensorsShape {
    private final int side;
    public SensorsSquare(int side) { this.side = side; }
    public int area() { return side * side; }
}

public class SensorsLspUtil {
    public static int total(SensorsShape[] shapes) {
        int t = 0;
        for (SensorsShape sh : shapes) t += sh.area();
        return t;
    }
}
