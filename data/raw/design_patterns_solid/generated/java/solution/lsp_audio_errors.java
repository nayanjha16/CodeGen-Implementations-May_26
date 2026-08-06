// DesignPatternsSolid | kind=solid | label=lsp | domain=audio | tier=errors
package org.example.patterns;

// LSP: subtypes usable wherever base audio shape is expected
abstract class AudioShape {
    public abstract int area();
}

class AudioRectangle extends AudioShape {
    protected int w, h;
    public AudioRectangle(int w, int h) { this.w = w; this.h = h; }
    public int area() { return w * h; }
}

class AudioSquare extends AudioShape {
    private final int side;
    public AudioSquare(int side) { this.side = side; }
    public int area() { return side * side; }
}

public class AudioLspUtil {
    public static int total(AudioShape[] shapes) {
        int t = 0;
        for (AudioShape sh : shapes) t += sh.area();
        return t;
    }
}
