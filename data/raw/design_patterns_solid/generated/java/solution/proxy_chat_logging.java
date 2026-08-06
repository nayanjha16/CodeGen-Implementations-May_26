// DesignPatternsSolid | kind=design_pattern | label=proxy | domain=chat | tier=logging
package org.example.patterns;

interface ChatService {
    String load(String id);
}

class ChatRealService implements ChatService {
    public String load(String id) { return "real-chat:" + id; }
}

public class ChatProxy implements ChatService {
    private ChatRealService real;
    private final boolean allowed;
    public ChatProxy(boolean allowed) { this.allowed = allowed; }
    public String load(String id) {
        if (!allowed) return "denied";
        if (real == null) real = new ChatRealService();
        return real.load(id);
    }
}
