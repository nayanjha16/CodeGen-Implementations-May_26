// DesignPatternsSolid | kind=design_pattern | label=proxy | domain=session | tier=minimal
package org.example.patterns;

interface SessionService {
    String load(String id);
}

class SessionRealService implements SessionService {
    public String load(String id) { return "real-session:" + id; }
}

public class SessionProxy implements SessionService {
    private SessionRealService real;
    private final boolean allowed;
    public SessionProxy(boolean allowed) { this.allowed = allowed; }
    public String load(String id) {
        if (!allowed) return "denied";
        if (real == null) real = new SessionRealService();
        return real.load(id);
    }
}
