// DesignPatternsSolid | kind=solid | label=lsp | domain=sync | tier=errors
package org.example.patterns;

// LSP: subtypes usable wherever base sync shape is expected
abstract class SyncShape {
    public abstract int area();
}

class SyncRectangle extends SyncShape {
    protected int w, h;
    public SyncRectangle(int w, int h) { this.w = w; this.h = h; }
    public int area() { return w * h; }
}

class SyncSquare extends SyncShape {
    private final int side;
    public SyncSquare(int side) { this.side = side; }
    public int area() { return side * side; }
}

public class SyncLspUtil {
    public static int total(SyncShape[] shapes) {
        int t = 0;
        for (SyncShape sh : shapes) t += sh.area();
        return t;
    }
}
