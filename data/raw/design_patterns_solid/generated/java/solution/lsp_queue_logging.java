// DesignPatternsSolid | kind=solid | label=lsp | domain=queue | tier=logging
package org.example.patterns;

// LSP: subtypes usable wherever base queue shape is expected
abstract class QueueShape {
    public abstract int area();
}

class QueueRectangle extends QueueShape {
    protected int w, h;
    public QueueRectangle(int w, int h) { this.w = w; this.h = h; }
    public int area() { return w * h; }
}

class QueueSquare extends QueueShape {
    private final int side;
    public QueueSquare(int side) { this.side = side; }
    public int area() { return side * side; }
}

public class QueueLspUtil {
    public static int total(QueueShape[] shapes) {
        int t = 0;
        for (QueueShape sh : shapes) t += sh.area();
        return t;
    }
}
