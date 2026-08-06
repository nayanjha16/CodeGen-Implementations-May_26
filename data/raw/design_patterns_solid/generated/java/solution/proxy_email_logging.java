// DesignPatternsSolid | kind=design_pattern | label=proxy | domain=email | tier=logging
package org.example.patterns;

interface EmailService {
    String load(String id);
}

class EmailRealService implements EmailService {
    public String load(String id) { return "real-email:" + id; }
}

public class EmailProxy implements EmailService {
    private EmailRealService real;
    private final boolean allowed;
    public EmailProxy(boolean allowed) { this.allowed = allowed; }
    public String load(String id) {
        if (!allowed) return "denied";
        if (real == null) real = new EmailRealService();
        return real.load(id);
    }
}
