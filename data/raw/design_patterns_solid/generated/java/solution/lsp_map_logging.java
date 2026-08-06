// DesignPatternsSolid | kind=solid | label=lsp | domain=map | tier=logging
package org.example.patterns;

// LSP: subtypes usable wherever base map shape is expected
abstract class MapShape {
    public abstract int area();
}

class MapRectangle extends MapShape {
    protected int w, h;
    public MapRectangle(int w, int h) { this.w = w; this.h = h; }
    public int area() { return w * h; }
}

class MapSquare extends MapShape {
    private final int side;
    public MapSquare(int side) { this.side = side; }
    public int area() { return side * side; }
}

public class MapLspUtil {
    public static int total(MapShape[] shapes) {
        int t = 0;
        for (MapShape sh : shapes) t += sh.area();
        return t;
    }
}
