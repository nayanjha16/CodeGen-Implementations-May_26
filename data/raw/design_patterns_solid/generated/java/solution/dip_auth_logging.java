// DesignPatternsSolid | kind=solid | label=dip | domain=auth | tier=logging
package org.example.patterns;

// DIP: high-level auth module depends on abstraction
interface AuthGateway {
    String send(String payload);
}

class AuthHttpGateway implements AuthGateway {
    public String send(String payload) { return "http-auth:" + payload; }
}

public class AuthAppService {
    private final AuthGateway gateway;
    public AuthAppService(AuthGateway gateway) { this.gateway = gateway; }
    public String publish(String payload) { return gateway.send(payload); }
}
