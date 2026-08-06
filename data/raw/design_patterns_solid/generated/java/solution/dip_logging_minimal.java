// DesignPatternsSolid | kind=solid | label=dip | domain=logging | tier=minimal
package org.example.patterns;

// DIP: high-level logging module depends on abstraction
interface LoggingGateway {
    String send(String payload);
}

class LoggingHttpGateway implements LoggingGateway {
    public String send(String payload) { return "http-logging:" + payload; }
}

public class LoggingAppService {
    private final LoggingGateway gateway;
    public LoggingAppService(LoggingGateway gateway) { this.gateway = gateway; }
    public String publish(String payload) { return gateway.send(payload); }
}
