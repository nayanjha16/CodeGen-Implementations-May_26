// DesignPatternsSolid | kind=design_pattern | label=proxy | domain=profile | tier=logging
package org.example.patterns;

interface ProfileService {
    String load(String id);
}

class ProfileRealService implements ProfileService {
    public String load(String id) { return "real-profile:" + id; }
}

public class ProfileProxy implements ProfileService {
    private ProfileRealService real;
    private final boolean allowed;
    public ProfileProxy(boolean allowed) { this.allowed = allowed; }
    public String load(String id) {
        if (!allowed) return "denied";
        if (real == null) real = new ProfileRealService();
        return real.load(id);
    }
}
