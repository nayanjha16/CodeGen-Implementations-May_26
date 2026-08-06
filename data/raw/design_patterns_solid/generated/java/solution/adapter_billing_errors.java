// DesignPatternsSolid | kind=design_pattern | label=adapter | domain=billing | tier=errors
package org.example.patterns;

class BillingLegacyApi {
    public String legacyFetch() { return "LEGACY-billing"; }
}

interface BillingTarget {
    String fetch();
}

public class BillingAdapter implements BillingTarget {
    private final BillingLegacyApi legacy;

    public BillingAdapter(BillingLegacyApi legacy) {
        this.legacy = legacy;
    }

    public String fetch() {
        String raw = legacy.legacyFetch();
        return raw.toLowerCase().replace("legacy-", "modern-");
    }
}
