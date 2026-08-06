// DesignPatternsSolid | kind=design_pattern | label=factory | domain=profile | tier=minimal
package org.example.patterns;

interface ProfileProduct {
    String operate();
}

class ProfileBasicProduct implements ProfileProduct {
    public String operate() { return "basic-profile"; }
}

class ProfilePremiumProduct implements ProfileProduct {
    public String operate() { return "premium-profile"; }
}

public class ProfileFactory {
    public ProfileProduct create(String type) {
        if ("premium".equalsIgnoreCase(type)) return new ProfilePremiumProduct();
        return new ProfileBasicProduct();
    }
}
