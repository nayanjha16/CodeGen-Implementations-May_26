// DesignPatternsSolid | kind=solid | label=lsp | domain=streaming | tier=minimal
package org.example.patterns;

// LSP: subtypes usable wherever base streaming shape is expected
abstract class StreamingShape {
    public abstract int area();
}

class StreamingRectangle extends StreamingShape {
    protected int w, h;
    public StreamingRectangle(int w, int h) { this.w = w; this.h = h; }
    public int area() { return w * h; }
}

class StreamingSquare extends StreamingShape {
    private final int side;
    public StreamingSquare(int side) { this.side = side; }
    public int area() { return side * side; }
}

public class StreamingLspUtil {
    public static int total(StreamingShape[] shapes) {
        int t = 0;
        for (StreamingShape sh : shapes) t += sh.area();
        return t;
    }
}
