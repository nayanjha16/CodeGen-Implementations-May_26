// DesignPatternsSolid | kind=solid | label=dip | domain=sms | tier=minimal
package org.example.patterns;

// DIP: high-level sms module depends on abstraction
interface SmsGateway {
    String send(String payload);
}

class SmsHttpGateway implements SmsGateway {
    public String send(String payload) { return "http-sms:" + payload; }
}

public class SmsAppService {
    private final SmsGateway gateway;
    public SmsAppService(SmsGateway gateway) { this.gateway = gateway; }
    public String publish(String payload) { return gateway.send(payload); }
}
