// DesignPatternsSolid | kind=solid | label=isp | domain=canvas | tier=errors
package org.example.patterns;

// ISP: small role interfaces for canvas
interface CanvasReadable {
    String read();
}
interface CanvasWritable {
    void write(String v);
}

class CanvasStore implements CanvasReadable, CanvasWritable {
    private String data = "";
    public String read() { return data; }
    public void write(String v) { data = "canvas:" + v; }
}

public class CanvasIspClient {
    public static String mirror(CanvasReadable r) { return r.read(); }
}
