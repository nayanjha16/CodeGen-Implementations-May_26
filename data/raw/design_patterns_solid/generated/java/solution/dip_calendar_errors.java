// DesignPatternsSolid | kind=solid | label=dip | domain=calendar | tier=errors
package org.example.patterns;

// DIP: high-level calendar module depends on abstraction
interface CalendarGateway {
    String send(String payload);
}

class CalendarHttpGateway implements CalendarGateway {
    public String send(String payload) { return "http-calendar:" + payload; }
}

public class CalendarAppService {
    private final CalendarGateway gateway;
    public CalendarAppService(CalendarGateway gateway) { this.gateway = gateway; }
    public String publish(String payload) { return gateway.send(payload); }
}
