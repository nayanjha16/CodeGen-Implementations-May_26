// DesignPatternsSolid | kind=design_pattern | label=adapter | domain=widgets | tier=logging
package org.example.patterns;

class WidgetsLegacyApi {
    public String legacyFetch() { return "LEGACY-widgets"; }
}

interface WidgetsTarget {
    String fetch();
}

public class WidgetsAdapter implements WidgetsTarget {
    private final WidgetsLegacyApi legacy;

    public WidgetsAdapter(WidgetsLegacyApi legacy) {
        this.legacy = legacy;
    }

    public String fetch() {
        String raw = legacy.legacyFetch();
        return raw.toLowerCase().replace("legacy-", "modern-");
    }
}
