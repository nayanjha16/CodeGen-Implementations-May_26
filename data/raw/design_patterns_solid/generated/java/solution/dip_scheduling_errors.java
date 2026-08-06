// DesignPatternsSolid | kind=solid | label=dip | domain=scheduling | tier=errors
package org.example.patterns;

// DIP: high-level scheduling module depends on abstraction
interface SchedulingGateway {
    String send(String payload);
}

class SchedulingHttpGateway implements SchedulingGateway {
    public String send(String payload) { return "http-scheduling:" + payload; }
}

public class SchedulingAppService {
    private final SchedulingGateway gateway;
    public SchedulingAppService(SchedulingGateway gateway) { this.gateway = gateway; }
    public String publish(String payload) { return gateway.send(payload); }
}
