// DesignPatternsSolid | kind=solid | label=lsp | domain=cache | tier=logging
package org.example.patterns;

// LSP: subtypes usable wherever base cache shape is expected
abstract class CacheShape {
    public abstract int area();
}

class CacheRectangle extends CacheShape {
    protected int w, h;
    public CacheRectangle(int w, int h) { this.w = w; this.h = h; }
    public int area() { return w * h; }
}

class CacheSquare extends CacheShape {
    private final int side;
    public CacheSquare(int side) { this.side = side; }
    public int area() { return side * side; }
}

public class CacheLspUtil {
    public static int total(CacheShape[] shapes) {
        int t = 0;
        for (CacheShape sh : shapes) t += sh.area();
        return t;
    }
}
