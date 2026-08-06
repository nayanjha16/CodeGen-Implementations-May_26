// DesignPatternsSolid | kind=solid | label=lsp | domain=license | tier=logging
package org.example.patterns;

// LSP: subtypes usable wherever base license shape is expected
abstract class LicenseShape {
    public abstract int area();
}

class LicenseRectangle extends LicenseShape {
    protected int w, h;
    public LicenseRectangle(int w, int h) { this.w = w; this.h = h; }
    public int area() { return w * h; }
}

class LicenseSquare extends LicenseShape {
    private final int side;
    public LicenseSquare(int side) { this.side = side; }
    public int area() { return side * side; }
}

public class LicenseLspUtil {
    public static int total(LicenseShape[] shapes) {
        int t = 0;
        for (LicenseShape sh : shapes) t += sh.area();
        return t;
    }
}
