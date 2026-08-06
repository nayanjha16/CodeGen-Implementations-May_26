// DesignPatternsSolid | kind=solid | label=isp | domain=license | tier=minimal
package org.example.patterns;

// ISP: small role interfaces for license
interface LicenseReadable {
    String read();
}
interface LicenseWritable {
    void write(String v);
}

class LicenseStore implements LicenseReadable, LicenseWritable {
    private String data = "";
    public String read() { return data; }
    public void write(String v) { data = "license:" + v; }
}

public class LicenseIspClient {
    public static String mirror(LicenseReadable r) { return r.read(); }
}
