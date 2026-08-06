// DesignPatternsSolid | kind=design_pattern | label=adapter | domain=metrics | tier=minimal
package org.example.patterns;

class MetricsLegacyApi {
    public String legacyFetch() { return "LEGACY-metrics"; }
}

interface MetricsTarget {
    String fetch();
}

public class MetricsAdapter implements MetricsTarget {
    private final MetricsLegacyApi legacy;

    public MetricsAdapter(MetricsLegacyApi legacy) {
        this.legacy = legacy;
    }

    public String fetch() {
        String raw = legacy.legacyFetch();
        return raw.toLowerCase().replace("legacy-", "modern-");
    }
}
