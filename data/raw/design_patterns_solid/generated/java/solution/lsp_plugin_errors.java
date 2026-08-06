// DesignPatternsSolid | kind=solid | label=lsp | domain=plugin | tier=errors
package org.example.patterns;

// LSP: subtypes usable wherever base plugin shape is expected
abstract class PluginShape {
    public abstract int area();
}

class PluginRectangle extends PluginShape {
    protected int w, h;
    public PluginRectangle(int w, int h) { this.w = w; this.h = h; }
    public int area() { return w * h; }
}

class PluginSquare extends PluginShape {
    private final int side;
    public PluginSquare(int side) { this.side = side; }
    public int area() { return side * side; }
}

public class PluginLspUtil {
    public static int total(PluginShape[] shapes) {
        int t = 0;
        for (PluginShape sh : shapes) t += sh.area();
        return t;
    }
}
