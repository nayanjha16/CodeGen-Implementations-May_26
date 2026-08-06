// DesignPatternsSolid | kind=solid | label=isp | domain=auth | tier=errors
package org.example.patterns;

// ISP: small role interfaces for auth
interface AuthReadable {
    String read();
}
interface AuthWritable {
    void write(String v);
}

class AuthStore implements AuthReadable, AuthWritable {
    private String data = "";
    public String read() { return data; }
    public void write(String v) { data = "auth:" + v; }
}

public class AuthIspClient {
    public static String mirror(AuthReadable r) { return r.read(); }
}
