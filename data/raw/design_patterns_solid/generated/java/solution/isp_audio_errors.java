// DesignPatternsSolid | kind=solid | label=isp | domain=audio | tier=errors
package org.example.patterns;

// ISP: small role interfaces for audio
interface AudioReadable {
    String read();
}
interface AudioWritable {
    void write(String v);
}

class AudioStore implements AudioReadable, AudioWritable {
    private String data = "";
    public String read() { return data; }
    public void write(String v) { data = "audio:" + v; }
}

public class AudioIspClient {
    public static String mirror(AudioReadable r) { return r.read(); }
}
