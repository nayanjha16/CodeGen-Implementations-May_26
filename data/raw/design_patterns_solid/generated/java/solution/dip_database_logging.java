// DesignPatternsSolid | kind=solid | label=dip | domain=database | tier=logging
package org.example.patterns;

// DIP: high-level database module depends on abstraction
interface DatabaseGateway {
    String send(String payload);
}

class DatabaseHttpGateway implements DatabaseGateway {
    public String send(String payload) { return "http-database:" + payload; }
}

public class DatabaseAppService {
    private final DatabaseGateway gateway;
    public DatabaseAppService(DatabaseGateway gateway) { this.gateway = gateway; }
    public String publish(String payload) { return gateway.send(payload); }
}
