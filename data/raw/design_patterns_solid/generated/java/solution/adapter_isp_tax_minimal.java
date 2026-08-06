// DesignPatternsSolid | kind=combo | label=adapter+isp | domain=tax | tier=minimal
package org.example.patterns;

class TaxLegacyApi {
    public String legacyFetch() { return "LEGACY-tax"; }
}

interface TaxTarget {
    String fetch();
}

public class TaxAdapter implements TaxTarget {
    private final TaxLegacyApi legacy;

    public TaxAdapter(TaxLegacyApi legacy) {
        this.legacy = legacy;
    }

    public String fetch() {
        String raw = legacy.legacyFetch();
        return raw.toLowerCase().replace("legacy-", "modern-");
    }
}
