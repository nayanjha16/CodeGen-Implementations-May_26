// DesignPatternsSolid | kind=design_pattern | label=factory | domain=auth | tier=minimal
package org.example.patterns;

interface AuthProduct {
    String operate();
}

class AuthBasicProduct implements AuthProduct {
    public String operate() { return "basic-auth"; }
}

class AuthPremiumProduct implements AuthProduct {
    public String operate() { return "premium-auth"; }
}

public class AuthFactory {
    public AuthProduct create(String type) {
        if ("premium".equalsIgnoreCase(type)) return new AuthPremiumProduct();
        return new AuthBasicProduct();
    }
}
