// DesignPatternsSolid | kind=combo | label=adapter+isp | domain=discount | tier=minimal
package org.example.patterns;

class DiscountLegacyApi {
    public String legacyFetch() { return "LEGACY-discount"; }
}

interface DiscountTarget {
    String fetch();
}

public class DiscountAdapter implements DiscountTarget {
    private final DiscountLegacyApi legacy;

    public DiscountAdapter(DiscountLegacyApi legacy) {
        this.legacy = legacy;
    }

    public String fetch() {
        String raw = legacy.legacyFetch();
        return raw.toLowerCase().replace("legacy-", "modern-");
    }
}
