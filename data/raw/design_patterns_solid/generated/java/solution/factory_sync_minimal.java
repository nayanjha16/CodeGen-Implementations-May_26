// DesignPatternsSolid | kind=design_pattern | label=factory | domain=sync | tier=minimal
package org.example.patterns;

interface SyncProduct {
    String operate();
}

class SyncBasicProduct implements SyncProduct {
    public String operate() { return "basic-sync"; }
}

class SyncPremiumProduct implements SyncProduct {
    public String operate() { return "premium-sync"; }
}

public class SyncFactory {
    public SyncProduct create(String type) {
        if ("premium".equalsIgnoreCase(type)) return new SyncPremiumProduct();
        return new SyncBasicProduct();
    }
}
