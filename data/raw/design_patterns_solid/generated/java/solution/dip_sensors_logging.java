// DesignPatternsSolid | kind=solid | label=dip | domain=sensors | tier=logging
package org.example.patterns;

// DIP: high-level sensors module depends on abstraction
interface SensorsGateway {
    String send(String payload);
}

class SensorsHttpGateway implements SensorsGateway {
    public String send(String payload) { return "http-sensors:" + payload; }
}

public class SensorsAppService {
    private final SensorsGateway gateway;
    public SensorsAppService(SensorsGateway gateway) { this.gateway = gateway; }
    public String publish(String payload) { return gateway.send(payload); }
}
