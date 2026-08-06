// DesignPatternsSolid | kind=solid | label=dip | domain=billing | tier=logging
package org.example.patterns;

// DIP: high-level billing module depends on abstraction
interface BillingGateway {
    String send(String payload);
}

class BillingHttpGateway implements BillingGateway {
    public String send(String payload) { return "http-billing:" + payload; }
}

public class BillingAppService {
    private final BillingGateway gateway;
    public BillingAppService(BillingGateway gateway) { this.gateway = gateway; }
    public String publish(String payload) { return gateway.send(payload); }
}
