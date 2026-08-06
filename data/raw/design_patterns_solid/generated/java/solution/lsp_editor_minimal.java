// DesignPatternsSolid | kind=solid | label=lsp | domain=editor | tier=minimal
package org.example.patterns;

// LSP: subtypes usable wherever base editor shape is expected
abstract class EditorShape {
    public abstract int area();
}

class EditorRectangle extends EditorShape {
    protected int w, h;
    public EditorRectangle(int w, int h) { this.w = w; this.h = h; }
    public int area() { return w * h; }
}

class EditorSquare extends EditorShape {
    private final int side;
    public EditorSquare(int side) { this.side = side; }
    public int area() { return side * side; }
}

public class EditorLspUtil {
    public static int total(EditorShape[] shapes) {
        int t = 0;
        for (EditorShape sh : shapes) t += sh.area();
        return t;
    }
}
