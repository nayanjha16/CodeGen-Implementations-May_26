// DesignPatternsSolid | kind=solid | label=lsp | domain=game | tier=errors
package org.example.patterns;

// LSP: subtypes usable wherever base game shape is expected
abstract class GameShape {
    public abstract int area();
}

class GameRectangle extends GameShape {
    protected int w, h;
    public GameRectangle(int w, int h) { this.w = w; this.h = h; }
    public int area() { return w * h; }
}

class GameSquare extends GameShape {
    private final int side;
    public GameSquare(int side) { this.side = side; }
    public int area() { return side * side; }
}

public class GameLspUtil {
    public static int total(GameShape[] shapes) {
        int t = 0;
        for (GameShape sh : shapes) t += sh.area();
        return t;
    }
}
