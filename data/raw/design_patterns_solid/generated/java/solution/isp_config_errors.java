// DesignPatternsSolid | kind=solid | label=isp | domain=config | tier=errors
package org.example.patterns;

// ISP: small role interfaces for config
interface ConfigReadable {
    String read();
}
interface ConfigWritable {
    void write(String v);
}

class ConfigStore implements ConfigReadable, ConfigWritable {
    private String data = "";
    public String read() { return data; }
    public void write(String v) { data = "config:" + v; }
}

public class ConfigIspClient {
    public static String mirror(ConfigReadable r) { return r.read(); }
}
