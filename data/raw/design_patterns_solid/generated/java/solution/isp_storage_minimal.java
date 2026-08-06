// DesignPatternsSolid | kind=solid | label=isp | domain=storage | tier=minimal
package org.example.patterns;

// ISP: small role interfaces for storage
interface StorageReadable {
    String read();
}
interface StorageWritable {
    void write(String v);
}

class StorageStore implements StorageReadable, StorageWritable {
    private String data = "";
    public String read() { return data; }
    public void write(String v) { data = "storage:" + v; }
}

public class StorageIspClient {
    public static String mirror(StorageReadable r) { return r.read(); }
}
