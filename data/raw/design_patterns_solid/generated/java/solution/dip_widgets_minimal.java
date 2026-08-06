// DesignPatternsSolid | kind=solid | label=dip | domain=widgets | tier=minimal
package org.example.patterns;

// DIP: high-level widgets module depends on abstraction
interface WidgetsGateway {
    String send(String payload);
}

class WidgetsHttpGateway implements WidgetsGateway {
    public String send(String payload) { return "http-widgets:" + payload; }
}

public class WidgetsAppService {
    private final WidgetsGateway gateway;
    public WidgetsAppService(WidgetsGateway gateway) { this.gateway = gateway; }
    public String publish(String payload) { return gateway.send(payload); }
}
