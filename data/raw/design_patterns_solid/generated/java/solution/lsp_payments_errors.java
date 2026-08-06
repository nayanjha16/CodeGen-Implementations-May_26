// DesignPatternsSolid | kind=solid | label=lsp | domain=payments | tier=errors
package org.example.patterns;

// LSP: subtypes usable wherever base payments shape is expected
abstract class PaymentsShape {
    public abstract int area();
}

class PaymentsRectangle extends PaymentsShape {
    protected int w, h;
    public PaymentsRectangle(int w, int h) { this.w = w; this.h = h; }
    public int area() { return w * h; }
}

class PaymentsSquare extends PaymentsShape {
    private final int side;
    public PaymentsSquare(int side) { this.side = side; }
    public int area() { return side * side; }
}

public class PaymentsLspUtil {
    public static int total(PaymentsShape[] shapes) {
        int t = 0;
        for (PaymentsShape sh : shapes) t += sh.area();
        return t;
    }
}
