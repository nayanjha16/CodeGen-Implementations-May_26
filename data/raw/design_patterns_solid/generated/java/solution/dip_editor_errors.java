// DesignPatternsSolid | kind=solid | label=dip | domain=editor | tier=errors
package org.example.patterns;

// DIP: high-level editor module depends on abstraction
interface EditorGateway {
    String send(String payload);
}

class EditorHttpGateway implements EditorGateway {
    public String send(String payload) { return "http-editor:" + payload; }
}

public class EditorAppService {
    private final EditorGateway gateway;
    public EditorAppService(EditorGateway gateway) { this.gateway = gateway; }
    public String publish(String payload) { return gateway.send(payload); }
}
