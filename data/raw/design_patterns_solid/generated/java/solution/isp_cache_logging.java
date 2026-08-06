// DesignPatternsSolid | kind=solid | label=isp | domain=cache | tier=logging
package org.example.patterns;

// ISP: small role interfaces for cache
interface CacheReadable {
    String read();
}
interface CacheWritable {
    void write(String v);
}

class CacheStore implements CacheReadable, CacheWritable {
    private String data = "";
    public String read() { return data; }
    public void write(String v) { data = "cache:" + v; }
}

public class CacheIspClient {
    public static String mirror(CacheReadable r) { return r.read(); }
}
