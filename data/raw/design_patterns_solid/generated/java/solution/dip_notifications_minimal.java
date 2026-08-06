// DesignPatternsSolid | kind=solid | label=dip | domain=notifications | tier=minimal
package org.example.patterns;

// DIP: high-level notifications module depends on abstraction
interface NotificationsGateway {
    String send(String payload);
}

class NotificationsHttpGateway implements NotificationsGateway {
    public String send(String payload) { return "http-notifications:" + payload; }
}

public class NotificationsAppService {
    private final NotificationsGateway gateway;
    public NotificationsAppService(NotificationsGateway gateway) { this.gateway = gateway; }
    public String publish(String payload) { return gateway.send(payload); }
}
