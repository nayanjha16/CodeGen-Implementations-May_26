// DesignPatternsSolid | kind=solid | label=isp | domain=game | tier=logging
package org.example.patterns;

// ISP: small role interfaces for game
interface GameReadable {
    String read();
}
interface GameWritable {
    void write(String v);
}

class GameStore implements GameReadable, GameWritable {
    private String data = "";
    public String read() { return data; }
    public void write(String v) { data = "game:" + v; }
}

public class GameIspClient {
    public static String mirror(GameReadable r) { return r.read(); }
}
