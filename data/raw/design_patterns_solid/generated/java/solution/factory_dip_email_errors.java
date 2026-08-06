// DesignPatternsSolid | kind=combo | label=factory+dip | domain=email | tier=errors
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
        if (type == null || type.isEmpty()) throw new IllegalArgumentException("type required");
        System.out.println("[log] create " + type);
        if ("premium".equalsIgnoreCase(type)) return new EmailPremiumProduct();
        return new EmailBasicProduct();
    }
}
