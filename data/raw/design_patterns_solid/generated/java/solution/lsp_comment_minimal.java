// DesignPatternsSolid | kind=solid | label=lsp | domain=comment | tier=minimal
package org.example.patterns;

// LSP: subtypes usable wherever base comment shape is expected
abstract class CommentShape {
    public abstract int area();
}

class CommentRectangle extends CommentShape {
    protected int w, h;
    public CommentRectangle(int w, int h) { this.w = w; this.h = h; }
    public int area() { return w * h; }
}

class CommentSquare extends CommentShape {
    private final int side;
    public CommentSquare(int side) { this.side = side; }
    public int area() { return side * side; }
}

public class CommentLspUtil {
    public static int total(CommentShape[] shapes) {
        int t = 0;
        for (CommentShape sh : shapes) t += sh.area();
        return t;
    }
}
