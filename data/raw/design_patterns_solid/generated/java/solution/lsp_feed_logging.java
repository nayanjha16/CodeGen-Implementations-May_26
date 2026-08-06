// DesignPatternsSolid | kind=solid | label=lsp | domain=feed | tier=logging
package org.example.patterns;

// LSP: subtypes usable wherever base feed shape is expected
abstract class FeedShape {
    public abstract int area();
}

class FeedRectangle extends FeedShape {
    protected int w, h;
    public FeedRectangle(int w, int h) { this.w = w; this.h = h; }
    public int area() { return w * h; }
}

class FeedSquare extends FeedShape {
    private final int side;
    public FeedSquare(int side) { this.side = side; }
    public int area() { return side * side; }
}

public class FeedLspUtil {
    public static int total(FeedShape[] shapes) {
        int t = 0;
        for (FeedShape sh : shapes) t += sh.area();
        return t;
    }
}
