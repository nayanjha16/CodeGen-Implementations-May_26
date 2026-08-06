// DesignPatternsSolid | kind=solid | label=lsp | domain=booking | tier=minimal
package org.example.patterns;

// LSP: subtypes usable wherever base booking shape is expected
abstract class BookingShape {
    public abstract int area();
}

class BookingRectangle extends BookingShape {
    protected int w, h;
    public BookingRectangle(int w, int h) { this.w = w; this.h = h; }
    public int area() { return w * h; }
}

class BookingSquare extends BookingShape {
    private final int side;
    public BookingSquare(int side) { this.side = side; }
    public int area() { return side * side; }
}

public class BookingLspUtil {
    public static int total(BookingShape[] shapes) {
        int t = 0;
        for (BookingShape sh : shapes) t += sh.area();
        return t;
    }
}
