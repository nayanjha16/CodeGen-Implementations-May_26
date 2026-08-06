// DesignPatternsSolid | kind=solid | label=dip | domain=ticket | tier=minimal
package org.example.patterns;

// DIP: high-level ticket module depends on abstraction
interface TicketGateway {
    String send(String payload);
}

class TicketHttpGateway implements TicketGateway {
    public String send(String payload) { return "http-ticket:" + payload; }
}

public class TicketAppService {
    private final TicketGateway gateway;
    public TicketAppService(TicketGateway gateway) { this.gateway = gateway; }
    public String publish(String payload) { return gateway.send(payload); }
}
