// DesignPatternsSolid | kind=solid | label=lsp | domain=database | tier=logging
package org.example.patterns;

// LSP: subtypes usable wherever base database shape is expected
abstract class DatabaseShape {
    public abstract int area();
}

class DatabaseRectangle extends DatabaseShape {
    protected int w, h;
    public DatabaseRectangle(int w, int h) { this.w = w; this.h = h; }
    public int area() { return w * h; }
}

class DatabaseSquare extends DatabaseShape {
    private final int side;
    public DatabaseSquare(int side) { this.side = side; }
    public int area() { return side * side; }
}

public class DatabaseLspUtil {
    public static int total(DatabaseShape[] shapes) {
        int t = 0;
        for (DatabaseShape sh : shapes) t += sh.area();
        return t;
    }
}
