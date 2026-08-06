// DesignPatternsSolid | kind=solid | label=isp | domain=database | tier=logging
package org.example.patterns;

// ISP: small role interfaces for database
interface DatabaseReadable {
    String read();
}
interface DatabaseWritable {
    void write(String v);
}

class DatabaseStore implements DatabaseReadable, DatabaseWritable {
    private String data = "";
    public String read() { return data; }
    public void write(String v) { data = "database:" + v; }
}

public class DatabaseIspClient {
    public static String mirror(DatabaseReadable r) { return r.read(); }
}
