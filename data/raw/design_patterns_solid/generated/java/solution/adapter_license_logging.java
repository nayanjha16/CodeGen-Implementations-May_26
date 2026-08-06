// DesignPatternsSolid | kind=design_pattern | label=adapter | domain=license | tier=logging
package org.example.patterns;

class LicenseLegacyApi {
    public String legacyFetch() { return "LEGACY-license"; }
}

interface LicenseTarget {
    String fetch();
}

public class LicenseAdapter implements LicenseTarget {
    private final LicenseLegacyApi legacy;

    public LicenseAdapter(LicenseLegacyApi legacy) {
        this.legacy = legacy;
    }

    public String fetch() {
        String raw = legacy.legacyFetch();
        return raw.toLowerCase().replace("legacy-", "modern-");
    }
}
