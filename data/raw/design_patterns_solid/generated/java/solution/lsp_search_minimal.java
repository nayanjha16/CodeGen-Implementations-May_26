// DesignPatternsSolid | kind=solid | label=lsp | domain=search | tier=minimal
package org.example.patterns;

// LSP: subtypes usable wherever base search shape is expected
abstract class SearchShape {
    public abstract int area();
}

class SearchRectangle extends SearchShape {
    protected int w, h;
    public SearchRectangle(int w, int h) { this.w = w; this.h = h; }
    public int area() { return w * h; }
}

class SearchSquare extends SearchShape {
    private final int side;
    public SearchSquare(int side) { this.side = side; }
    public int area() { return side * side; }
}

public class SearchLspUtil {
    public static int total(SearchShape[] shapes) {
        int t = 0;
        for (SearchShape sh : shapes) t += sh.area();
        return t;
    }
}
