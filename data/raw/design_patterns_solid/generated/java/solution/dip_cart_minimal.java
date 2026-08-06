// DesignPatternsSolid | kind=solid | label=dip | domain=cart | tier=minimal
package org.example.patterns;

// DIP: high-level cart module depends on abstraction
interface CartGateway {
    String send(String payload);
}

class CartHttpGateway implements CartGateway {
    public String send(String payload) { return "http-cart:" + payload; }
}

public class CartAppService {
    private final CartGateway gateway;
    public CartAppService(CartGateway gateway) { this.gateway = gateway; }
    public String publish(String payload) { return gateway.send(payload); }
}
