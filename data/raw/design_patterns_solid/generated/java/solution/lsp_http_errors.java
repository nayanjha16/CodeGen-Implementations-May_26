// DesignPatternsSolid | kind=solid | label=lsp | domain=http | tier=errors
package org.example.patterns;

// LSP: subtypes usable wherever base http shape is expected
abstract class HttpShape {
    public abstract int area();
}

class HttpRectangle extends HttpShape {
    protected int w, h;
    public HttpRectangle(int w, int h) { this.w = w; this.h = h; }
    public int area() { return w * h; }
}

class HttpSquare extends HttpShape {
    private final int side;
    public HttpSquare(int side) { this.side = side; }
    public int area() { return side * side; }
}

public class HttpLspUtil {
    public static int total(HttpShape[] shapes) {
        int t = 0;
        for (HttpShape sh : shapes) t += sh.area();
        return t;
    }
}
