// DesignPatternsSolid | kind=solid | label=lsp | domain=chat | tier=errors
package org.example.patterns;

// LSP: subtypes usable wherever base chat shape is expected
abstract class ChatShape {
    public abstract int area();
}

class ChatRectangle extends ChatShape {
    protected int w, h;
    public ChatRectangle(int w, int h) { this.w = w; this.h = h; }
    public int area() { return w * h; }
}

class ChatSquare extends ChatShape {
    private final int side;
    public ChatSquare(int side) { this.side = side; }
    public int area() { return side * side; }
}

public class ChatLspUtil {
    public static int total(ChatShape[] shapes) {
        int t = 0;
        for (ChatShape sh : shapes) t += sh.area();
        return t;
    }
}
