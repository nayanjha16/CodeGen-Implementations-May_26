// DesignPatternsSolid | kind=solid | label=dip | domain=http | tier=errors
package org.example.patterns;

// DIP: high-level http module depends on abstraction
interface HttpGateway {
    String send(String payload);
}

class HttpHttpGateway implements HttpGateway {
    public String send(String payload) { return "http-http:" + payload; }
}

public class HttpAppService {
    private final HttpGateway gateway;
    public HttpAppService(HttpGateway gateway) { this.gateway = gateway; }
    public String publish(String payload) { return gateway.send(payload); }
}
