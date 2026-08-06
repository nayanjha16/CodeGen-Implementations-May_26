// DesignPatternsSolid | kind=combo | label=factory+dip | domain=session | tier=logging
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
        System.out.println("[log] create " + type);
        if ("premium".equalsIgnoreCase(type)) return new SessionPremiumProduct();
        return new SessionBasicProduct();
    }
}
