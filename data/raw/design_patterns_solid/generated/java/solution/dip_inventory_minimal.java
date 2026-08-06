// DesignPatternsSolid | kind=solid | label=dip | domain=inventory | tier=minimal
package org.example.patterns;

// DIP: high-level inventory module depends on abstraction
interface InventoryGateway {
    String send(String payload);
}

class InventoryHttpGateway implements InventoryGateway {
    public String send(String payload) { return "http-inventory:" + payload; }
}

public class InventoryAppService {
    private final InventoryGateway gateway;
    public InventoryAppService(InventoryGateway gateway) { this.gateway = gateway; }
    public String publish(String payload) { return gateway.send(payload); }
}
