// DesignPatternsSolid | kind=solid | label=dip | domain=notes | tier=errors
package org.example.patterns;

// DIP: high-level notes module depends on abstraction
interface NotesGateway {
    String send(String payload);
}

class NotesHttpGateway implements NotesGateway {
    public String send(String payload) { return "http-notes:" + payload; }
}

public class NotesAppService {
    private final NotesGateway gateway;
    public NotesAppService(NotesGateway gateway) { this.gateway = gateway; }
    public String publish(String payload) { return gateway.send(payload); }
}
