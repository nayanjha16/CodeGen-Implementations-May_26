// DesignPatternsSolid | kind=solid | label=dip | domain=session | tier=logging
package org.example.patterns;

// DIP: high-level session module depends on abstraction
interface SessionGateway {
    String send(String payload);
}

class SessionHttpGateway implements SessionGateway {
    public String send(String payload) { return "http-session:" + payload; }
}

public class SessionAppService {
    private final SessionGateway gateway;
    public SessionAppService(SessionGateway gateway) { this.gateway = gateway; }
    public String publish(String payload) { return gateway.send(payload); }
}
