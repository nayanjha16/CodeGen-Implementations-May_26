// DesignPatternsSolid | kind=solid | label=dip | domain=shipping | tier=logging
package org.example.patterns;

// DIP: high-level shipping module depends on abstraction
interface ShippingGateway {
    String send(String payload);
}

class ShippingHttpGateway implements ShippingGateway {
    public String send(String payload) { return "http-shipping:" + payload; }
}

public class ShippingAppService {
    private final ShippingGateway gateway;
    public ShippingAppService(ShippingGateway gateway) { this.gateway = gateway; }
    public String publish(String payload) { return gateway.send(payload); }
}
