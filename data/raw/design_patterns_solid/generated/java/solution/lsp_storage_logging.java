// DesignPatternsSolid | kind=solid | label=lsp | domain=storage | tier=logging
package org.example.patterns;

// LSP: subtypes usable wherever base storage shape is expected
abstract class StorageShape {
    public abstract int area();
}

class StorageRectangle extends StorageShape {
    protected int w, h;
    public StorageRectangle(int w, int h) { this.w = w; this.h = h; }
    public int area() { return w * h; }
}

class StorageSquare extends StorageShape {
    private final int side;
    public StorageSquare(int side) { this.side = side; }
    public int area() { return side * side; }
}

public class StorageLspUtil {
    public static int total(StorageShape[] shapes) {
        int t = 0;
        for (StorageShape sh : shapes) t += sh.area();
        return t;
    }
}
