// DesignPatternsSolid | kind=combo | label=factory+dip | domain=billing | tier=logging
package org.example.patterns;

interface BillingProduct {
    String operate();
}

class BillingBasicProduct implements BillingProduct {
    public String operate() { return "basic-billing"; }
}

class BillingPremiumProduct implements BillingProduct {
    public String operate() { return "premium-billing"; }
}

public class BillingFactory {
    public BillingProduct create(String type) {
        System.out.println("[log] create " + type);
        if ("premium".equalsIgnoreCase(type)) return new BillingPremiumProduct();
        return new BillingBasicProduct();
    }
}
