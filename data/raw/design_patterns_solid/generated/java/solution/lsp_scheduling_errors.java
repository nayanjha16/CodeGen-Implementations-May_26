// DesignPatternsSolid | kind=solid | label=lsp | domain=scheduling | tier=errors
package org.example.patterns;

// LSP: subtypes usable wherever base scheduling shape is expected
abstract class SchedulingShape {
    public abstract int area();
}

class SchedulingRectangle extends SchedulingShape {
    protected int w, h;
    public SchedulingRectangle(int w, int h) { this.w = w; this.h = h; }
    public int area() { return w * h; }
}

class SchedulingSquare extends SchedulingShape {
    private final int side;
    public SchedulingSquare(int side) { this.side = side; }
    public int area() { return side * side; }
}

public class SchedulingLspUtil {
    public static int total(SchedulingShape[] shapes) {
        int t = 0;
        for (SchedulingShape sh : shapes) t += sh.area();
        return t;
    }
}
