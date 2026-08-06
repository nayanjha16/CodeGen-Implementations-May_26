// DesignPatternsSolid | kind=design_pattern | label=factory | domain=email | tier=minimal
package org.example.patterns;

interface EmailProduct {
    String operate();
}

class EmailBasicProduct implements EmailProduct {
    public String operate() { return "basic-email"; }
}

class EmailPremiumProduct implements EmailProduct {
    public String operate() { return "premium-email"; }
}

public class EmailFactory {
    public EmailProduct create(String type) {
        if ("premium".equalsIgnoreCase(type)) return new EmailPremiumProduct();
        return new EmailBasicProduct();
    }
}
