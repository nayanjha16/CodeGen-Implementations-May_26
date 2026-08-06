// DesignPatternsSolid | kind=solid | label=dip | domain=canvas | tier=minimal
package org.example.patterns;

// DIP: high-level canvas module depends on abstraction
interface CanvasGateway {
    String send(String payload);
}

class CanvasHttpGateway implements CanvasGateway {
    public String send(String payload) { return "http-canvas:" + payload; }
}

public class CanvasAppService {
    private final CanvasGateway gateway;
    public CanvasAppService(CanvasGateway gateway) { this.gateway = gateway; }
    public String publish(String payload) { return gateway.send(payload); }
}
