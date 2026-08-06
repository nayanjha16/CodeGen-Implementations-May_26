// DesignPatternsSolid | kind=solid | label=isp | domain=ticket | tier=minimal
package org.example.patterns;

// ISP: small role interfaces for ticket
interface TicketReadable {
    String read();
}
interface TicketWritable {
    void write(String v);
}

class TicketStore implements TicketReadable, TicketWritable {
    private String data = "";
    public String read() { return data; }
    public void write(String v) { data = "ticket:" + v; }
}

public class TicketIspClient {
    public static String mirror(TicketReadable r) { return r.read(); }
}
