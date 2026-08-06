// DesignPatternsSolid | kind=solid | label=dip | domain=sync | tier=errors
package org.example.patterns;

// DIP: high-level sync module depends on abstraction
interface SyncGateway {
    String send(String payload);
}

class SyncHttpGateway implements SyncGateway {
    public String send(String payload) { return "http-sync:" + payload; }
}

public class SyncAppService {
    private final SyncGateway gateway;
    public SyncAppService(SyncGateway gateway) { this.gateway = gateway; }
    public String publish(String payload) { return gateway.send(payload); }
}
