// DesignPatternsSolid | kind=solid | label=lsp | domain=logging | tier=logging
package org.example.patterns;

// LSP: subtypes usable wherever base logging shape is expected
abstract class LoggingShape {
    public abstract int area();
}

class LoggingRectangle extends LoggingShape {
    protected int w, h;
    public LoggingRectangle(int w, int h) { this.w = w; this.h = h; }
    public int area() { return w * h; }
}

class LoggingSquare extends LoggingShape {
    private final int side;
    public LoggingSquare(int side) { this.side = side; }
    public int area() { return side * side; }
}

public class LoggingLspUtil {
    public static int total(LoggingShape[] shapes) {
        int t = 0;
        for (LoggingShape sh : shapes) t += sh.area();
        return t;
    }
}
