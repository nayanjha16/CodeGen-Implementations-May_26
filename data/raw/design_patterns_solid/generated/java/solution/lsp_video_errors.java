// DesignPatternsSolid | kind=solid | label=lsp | domain=video | tier=errors
package org.example.patterns;

// LSP: subtypes usable wherever base video shape is expected
abstract class VideoShape {
    public abstract int area();
}

class VideoRectangle extends VideoShape {
    protected int w, h;
    public VideoRectangle(int w, int h) { this.w = w; this.h = h; }
    public int area() { return w * h; }
}

class VideoSquare extends VideoShape {
    private final int side;
    public VideoSquare(int side) { this.side = side; }
    public int area() { return side * side; }
}

public class VideoLspUtil {
    public static int total(VideoShape[] shapes) {
        int t = 0;
        for (VideoShape sh : shapes) t += sh.area();
        return t;
    }
}
