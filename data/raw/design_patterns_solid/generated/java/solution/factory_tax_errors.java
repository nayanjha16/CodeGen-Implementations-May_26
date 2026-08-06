// DesignPatternsSolid | kind=design_pattern | label=factory | domain=tax | tier=errors
package org.example.patterns;

interface TaxProduct {
    String operate();
}

class TaxBasicProduct implements TaxProduct {
    public String operate() { return "basic-tax"; }
}

class TaxPremiumProduct implements TaxProduct {
    public String operate() { return "premium-tax"; }
}

public class TaxFactory {
    public TaxProduct create(String type) {
        if (type == null || type.isEmpty()) throw new IllegalArgumentException("type required");
        System.out.println("[log] create " + type);
        if ("premium".equalsIgnoreCase(type)) return new TaxPremiumProduct();
        return new TaxBasicProduct();
    }
}
