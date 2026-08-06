// DesignPatternsSolid | kind=solid | label=isp | domain=map | tier=errors
package org.example.patterns;

// ISP: small role interfaces for map
interface MapReadable {
    String read();
}
interface MapWritable {
    void write(String v);
}

class MapStore implements MapReadable, MapWritable {
    private String data = "";
    public String read() { return data; }
    public void write(String v) { data = "map:" + v; }
}

public class MapIspClient {
    public static String mirror(MapReadable r) { return r.read(); }
}
