// DesignPatternsSolid | kind=solid | label=dip | domain=feed | tier=minimal
package org.example.patterns;

// DIP: high-level feed module depends on abstraction
interface FeedGateway {
    String send(String payload);
}

class FeedHttpGateway implements FeedGateway {
    public String send(String payload) { return "http-feed:" + payload; }
}

public class FeedAppService {
    private final FeedGateway gateway;
    public FeedAppService(FeedGateway gateway) { this.gateway = gateway; }
    public String publish(String payload) { return gateway.send(payload); }
}
