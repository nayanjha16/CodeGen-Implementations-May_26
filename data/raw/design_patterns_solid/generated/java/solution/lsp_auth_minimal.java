// DesignPatternsSolid | kind=solid | label=lsp | domain=auth | tier=minimal
package org.example.patterns;

// LSP: subtypes usable wherever base auth shape is expected
abstract class AuthShape {
    public abstract int area();
}

class AuthRectangle extends AuthShape {
    protected int w, h;
    public AuthRectangle(int w, int h) { this.w = w; this.h = h; }
    public int area() { return w * h; }
}

class AuthSquare extends AuthShape {
    private final int side;
    public AuthSquare(int side) { this.side = side; }
    public int area() { return side * side; }
}

public class AuthLspUtil {
    public static int total(AuthShape[] shapes) {
        int t = 0;
        for (AuthShape sh : shapes) t += sh.area();
        return t;
    }
}
