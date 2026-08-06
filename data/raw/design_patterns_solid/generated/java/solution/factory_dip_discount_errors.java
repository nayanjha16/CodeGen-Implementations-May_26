// DesignPatternsSolid | kind=combo | label=factory+dip | domain=discount | tier=errors
package org.example.patterns;

interface DiscountProduct {
    String operate();
}

class DiscountBasicProduct implements DiscountProduct {
    public String operate() { return "basic-discount"; }
}

class DiscountPremiumProduct implements DiscountProduct {
    public String operate() { return "premium-discount"; }
}

public class DiscountFactory {
    public DiscountProduct create(String type) {
        if (type == null || type.isEmpty()) throw new IllegalArgumentException("type required");
        System.out.println("[log] create " + type);
        if ("premium".equalsIgnoreCase(type)) return new DiscountPremiumProduct();
        return new DiscountBasicProduct();
    }
}
