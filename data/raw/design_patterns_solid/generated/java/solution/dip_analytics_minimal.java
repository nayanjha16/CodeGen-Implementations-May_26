// DesignPatternsSolid | kind=solid | label=dip | domain=analytics | tier=minimal
package org.example.patterns;

// DIP: high-level analytics module depends on abstraction
interface AnalyticsGateway {
    String send(String payload);
}

class AnalyticsHttpGateway implements AnalyticsGateway {
    public String send(String payload) { return "http-analytics:" + payload; }
}

public class AnalyticsAppService {
    private final AnalyticsGateway gateway;
    public AnalyticsAppService(AnalyticsGateway gateway) { this.gateway = gateway; }
    public String publish(String payload) { return gateway.send(payload); }
}
