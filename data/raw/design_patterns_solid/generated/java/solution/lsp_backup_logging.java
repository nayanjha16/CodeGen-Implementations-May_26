// DesignPatternsSolid | kind=solid | label=lsp | domain=backup | tier=logging
package org.example.patterns;

// LSP: subtypes usable wherever base backup shape is expected
abstract class BackupShape {
    public abstract int area();
}

class BackupRectangle extends BackupShape {
    protected int w, h;
    public BackupRectangle(int w, int h) { this.w = w; this.h = h; }
    public int area() { return w * h; }
}

class BackupSquare extends BackupShape {
    private final int side;
    public BackupSquare(int side) { this.side = side; }
    public int area() { return side * side; }
}

public class BackupLspUtil {
    public static int total(BackupShape[] shapes) {
        int t = 0;
        for (BackupShape sh : shapes) t += sh.area();
        return t;
    }
}
