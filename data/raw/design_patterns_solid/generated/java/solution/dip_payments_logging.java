// DesignPatternsSolid | kind=solid | label=dip | domain=payments | tier=logging
package org.example.patterns;

// DIP: high-level payments module depends on abstraction
interface PaymentsGateway {
    String send(String payload);
}

class PaymentsHttpGateway implements PaymentsGateway {
    public String send(String payload) { return "http-payments:" + payload; }
}

public class PaymentsAppService {
    private final PaymentsGateway gateway;
    public PaymentsAppService(PaymentsGateway gateway) { this.gateway = gateway; }
    public String publish(String payload) { return gateway.send(payload); }
}
