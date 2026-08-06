// DesignPatternsSolid | kind=solid | label=lsp | domain=notifications | tier=logging
package org.example.patterns;

// LSP: subtypes usable wherever base notifications shape is expected
abstract class NotificationsShape {
    public abstract int area();
}

class NotificationsRectangle extends NotificationsShape {
    protected int w, h;
    public NotificationsRectangle(int w, int h) { this.w = w; this.h = h; }
    public int area() { return w * h; }
}

class NotificationsSquare extends NotificationsShape {
    private final int side;
    public NotificationsSquare(int side) { this.side = side; }
    public int area() { return side * side; }
}

public class NotificationsLspUtil {
    public static int total(NotificationsShape[] shapes) {
        int t = 0;
        for (NotificationsShape sh : shapes) t += sh.area();
        return t;
    }
}
