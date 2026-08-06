// DesignPatternsSolid | kind=design_pattern | label=adapter | domain=sync | tier=errors
package org.example.patterns;

class SyncLegacyApi {
    public String legacyFetch() { return "LEGACY-sync"; }
}

interface SyncTarget {
    String fetch();
}

public class SyncAdapter implements SyncTarget {
    private final SyncLegacyApi legacy;

    public SyncAdapter(SyncLegacyApi legacy) {
        this.legacy = legacy;
    }

    public String fetch() {
        String raw = legacy.legacyFetch();
        return raw.toLowerCase().replace("legacy-", "modern-");
    }
}
