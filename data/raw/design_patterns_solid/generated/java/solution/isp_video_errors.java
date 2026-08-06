// DesignPatternsSolid | kind=solid | label=isp | domain=video | tier=errors
package org.example.patterns;

// ISP: small role interfaces for video
interface VideoReadable {
    String read();
}
interface VideoWritable {
    void write(String v);
}

class VideoStore implements VideoReadable, VideoWritable {
    private String data = "";
    public String read() { return data; }
    public void write(String v) { data = "video:" + v; }
}

public class VideoIspClient {
    public static String mirror(VideoReadable r) { return r.read(); }
}
