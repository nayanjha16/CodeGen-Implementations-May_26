// DesignPatternsSolid | kind=design_pattern | label=proxy | domain=auth | tier=errors
package org.example.patterns;

interface AuthService {
    String load(String id);
}

class AuthRealService implements AuthService {
    public String load(String id) { return "real-auth:" + id; }
}

public class AuthProxy implements AuthService {
    private AuthRealService real;
    private final boolean allowed;
    public AuthProxy(boolean allowed) { this.allowed = allowed; }
    public String load(String id) {
        if (!allowed) return "denied";
        if (real == null) real = new AuthRealService();
        return real.load(id);
    }
}
