// DesignPatternsSolid | kind=solid | label=lsp | domain=config | tier=errors
package org.example.patterns;

// LSP: subtypes usable wherever base config shape is expected
abstract class ConfigShape {
    public abstract int area();
}

class ConfigRectangle extends ConfigShape {
    protected int w, h;
    public ConfigRectangle(int w, int h) { this.w = w; this.h = h; }
    public int area() { return w * h; }
}

class ConfigSquare extends ConfigShape {
    private final int side;
    public ConfigSquare(int side) { this.side = side; }
    public int area() { return side * side; }
}

public class ConfigLspUtil {
    public static int total(ConfigShape[] shapes) {
        int t = 0;
        for (ConfigShape sh : shapes) t += sh.area();
        return t;
    }
}
