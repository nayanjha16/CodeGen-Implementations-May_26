// DesignPatternsSolid | kind=solid | label=dip | domain=map | tier=errors
package org.example.patterns;

// DIP: high-level map module depends on abstraction
interface MapGateway {
    String send(String payload);
}

class MapHttpGateway implements MapGateway {
    public String send(String payload) { return "http-map:" + payload; }
}

public class MapAppService {
    private final MapGateway gateway;
    public MapAppService(MapGateway gateway) { this.gateway = gateway; }
    public String publish(String payload) { return gateway.send(payload); }
}
