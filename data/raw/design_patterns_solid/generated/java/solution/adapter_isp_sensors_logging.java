// DesignPatternsSolid | kind=combo | label=adapter+isp | domain=sensors | tier=logging
package org.example.patterns;

class SensorsLegacyApi {
    public String legacyFetch() { return "LEGACY-sensors"; }
}

interface SensorsTarget {
    String fetch();
}

public class SensorsAdapter implements SensorsTarget {
    private final SensorsLegacyApi legacy;

    public SensorsAdapter(SensorsLegacyApi legacy) {
        this.legacy = legacy;
    }

    public String fetch() {
        String raw = legacy.legacyFetch();
        return raw.toLowerCase().replace("legacy-", "modern-");
    }
}
