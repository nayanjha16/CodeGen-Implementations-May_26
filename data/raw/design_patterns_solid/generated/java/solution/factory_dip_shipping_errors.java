// DesignPatternsSolid | kind=combo | label=factory+dip | domain=shipping | tier=errors
package org.example.patterns;

interface ShippingProduct {
    String operate();
}

class ShippingBasicProduct implements ShippingProduct {
    public String operate() { return "basic-shipping"; }
}

class ShippingPremiumProduct implements ShippingProduct {
    public String operate() { return "premium-shipping"; }
}

public class ShippingFactory {
    public ShippingProduct create(String type) {
        if (type == null || type.isEmpty()) throw new IllegalArgumentException("type required");
        System.out.println("[log] create " + type);
        if ("premium".equalsIgnoreCase(type)) return new ShippingPremiumProduct();
        return new ShippingBasicProduct();
    }
}
