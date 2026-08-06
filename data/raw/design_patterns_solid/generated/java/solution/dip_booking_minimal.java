// DesignPatternsSolid | kind=solid | label=dip | domain=booking | tier=minimal
package org.example.patterns;

// DIP: high-level booking module depends on abstraction
interface BookingGateway {
    String send(String payload);
}

class BookingHttpGateway implements BookingGateway {
    public String send(String payload) { return "http-booking:" + payload; }
}

public class BookingAppService {
    private final BookingGateway gateway;
    public BookingAppService(BookingGateway gateway) { this.gateway = gateway; }
    public String publish(String payload) { return gateway.send(payload); }
}
