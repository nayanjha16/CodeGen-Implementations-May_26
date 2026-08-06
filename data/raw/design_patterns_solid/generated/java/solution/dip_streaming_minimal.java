// DesignPatternsSolid | kind=solid | label=dip | domain=streaming | tier=minimal
package org.example.patterns;

// DIP: high-level streaming module depends on abstraction
interface StreamingGateway {
    String send(String payload);
}

class StreamingHttpGateway implements StreamingGateway {
    public String send(String payload) { return "http-streaming:" + payload; }
}

public class StreamingAppService {
    private final StreamingGateway gateway;
    public StreamingAppService(StreamingGateway gateway) { this.gateway = gateway; }
    public String publish(String payload) { return gateway.send(payload); }
}
