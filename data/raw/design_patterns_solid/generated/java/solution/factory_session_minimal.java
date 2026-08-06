// DesignPatternsSolid | kind=design_pattern | label=factory | domain=session | tier=minimal
package org.example.patterns;

interface SessionProduct {
    String operate();
}

class SessionBasicProduct implements SessionProduct {
    public String operate() { return "basic-session"; }
}

class SessionPremiumProduct implements SessionProduct {
    public String operate() { return "premium-session"; }
}

public class SessionFactory {
    public SessionProduct create(String type) {
        if ("premium".equalsIgnoreCase(type)) return new SessionPremiumProduct();
        return new SessionBasicProduct();
    }
}
