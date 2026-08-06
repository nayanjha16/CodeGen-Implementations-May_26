// DesignPatternsSolid | kind=solid | label=isp | domain=inventory | tier=minimal
package org.example.patterns;

// ISP: small role interfaces for inventory
interface InventoryReadable {
    String read();
}
interface InventoryWritable {
    void write(String v);
}

class InventoryStore implements InventoryReadable, InventoryWritable {
    private String data = "";
    public String read() { return data; }
    public void write(String v) { data = "inventory:" + v; }
}

public class InventoryIspClient {
    public static String mirror(InventoryReadable r) { return r.read(); }
}
