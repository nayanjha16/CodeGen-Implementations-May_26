// DesignPatternsSolid | kind=solid | label=isp | domain=profile | tier=minimal
package org.example.patterns;

// ISP: small role interfaces for profile
interface ProfileReadable {
    String read();
}
interface ProfileWritable {
    void write(String v);
}

class ProfileStore implements ProfileReadable, ProfileWritable {
    private String data = "";
    public String read() { return data; }
    public void write(String v) { data = "profile:" + v; }
}

public class ProfileIspClient {
    public static String mirror(ProfileReadable r) { return r.read(); }
}
