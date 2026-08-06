// DesignPatternsSolid | kind=combo | label=adapter+isp | domain=analytics | tier=logging
package org.example.patterns;

class AnalyticsLegacyApi {
    public String legacyFetch() { return "LEGACY-analytics"; }
}

interface AnalyticsTarget {
    String fetch();
}

public class AnalyticsAdapter implements AnalyticsTarget {
    private final AnalyticsLegacyApi legacy;

    public AnalyticsAdapter(AnalyticsLegacyApi legacy) {
        this.legacy = legacy;
    }

    public String fetch() {
        String raw = legacy.legacyFetch();
        return raw.toLowerCase().replace("legacy-", "modern-");
    }
}
