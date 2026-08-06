// DesignPatternsSolid | kind=solid | label=lsp | domain=profile | tier=minimal
package org.example.patterns;

// LSP: subtypes usable wherever base profile shape is expected
abstract class ProfileShape {
    public abstract int area();
}

class ProfileRectangle extends ProfileShape {
    protected int w, h;
    public ProfileRectangle(int w, int h) { this.w = w; this.h = h; }
    public int area() { return w * h; }
}

class ProfileSquare extends ProfileShape {
    private final int side;
    public ProfileSquare(int side) { this.side = side; }
    public int area() { return side * side; }
}

public class ProfileLspUtil {
    public static int total(ProfileShape[] shapes) {
        int t = 0;
        for (ProfileShape sh : shapes) t += sh.area();
        return t;
    }
}
