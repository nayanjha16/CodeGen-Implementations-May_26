// DesignPatternsSolid | kind=solid | label=isp | domain=plugin | tier=errors
package org.example.patterns;

// ISP: small role interfaces for plugin
interface PluginReadable {
    String read();
}
interface PluginWritable {
    void write(String v);
}

class PluginStore implements PluginReadable, PluginWritable {
    private String data = "";
    public String read() { return data; }
    public void write(String v) { data = "plugin:" + v; }
}

public class PluginIspClient {
    public static String mirror(PluginReadable r) { return r.read(); }
}
