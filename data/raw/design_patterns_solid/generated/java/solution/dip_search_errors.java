// DesignPatternsSolid | kind=solid | label=dip | domain=search | tier=errors
package org.example.patterns;

// DIP: high-level search module depends on abstraction
interface SearchGateway {
    String send(String payload);
}

class SearchHttpGateway implements SearchGateway {
    public String send(String payload) { return "http-search:" + payload; }
}

public class SearchAppService {
    private final SearchGateway gateway;
    public SearchAppService(SearchGateway gateway) { this.gateway = gateway; }
    public String publish(String payload) { return gateway.send(payload); }
}
