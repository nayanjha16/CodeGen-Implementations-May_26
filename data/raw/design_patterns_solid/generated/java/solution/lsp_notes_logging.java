// DesignPatternsSolid | kind=solid | label=lsp | domain=notes | tier=logging
package org.example.patterns;

// LSP: subtypes usable wherever base notes shape is expected
abstract class NotesShape {
    public abstract int area();
}

class NotesRectangle extends NotesShape {
    protected int w, h;
    public NotesRectangle(int w, int h) { this.w = w; this.h = h; }
    public int area() { return w * h; }
}

class NotesSquare extends NotesShape {
    private final int side;
    public NotesSquare(int side) { this.side = side; }
    public int area() { return side * side; }
}

public class NotesLspUtil {
    public static int total(NotesShape[] shapes) {
        int t = 0;
        for (NotesShape sh : shapes) t += sh.area();
        return t;
    }
}
