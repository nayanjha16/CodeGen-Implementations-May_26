// DesignPatternsSolid | kind=solid | label=lsp | domain=email | tier=minimal
package org.example.patterns;

// LSP: subtypes usable wherever base email shape is expected
abstract class EmailShape {
    public abstract int area();
}

class EmailRectangle extends EmailShape {
    protected int w, h;
    public EmailRectangle(int w, int h) { this.w = w; this.h = h; }
    public int area() { return w * h; }
}

class EmailSquare extends EmailShape {
    private final int side;
    public EmailSquare(int side) { this.side = side; }
    public int area() { return side * side; }
}

public class EmailLspUtil {
    public static int total(EmailShape[] shapes) {
        int t = 0;
        for (EmailShape sh : shapes) t += sh.area();
        return t;
    }
}
