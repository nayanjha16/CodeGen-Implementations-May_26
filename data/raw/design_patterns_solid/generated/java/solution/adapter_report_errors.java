// DesignPatternsSolid | kind=design_pattern | label=adapter | domain=report | tier=errors
package org.example.patterns;

class ReportLegacyApi {
    public String legacyFetch() { return "LEGACY-report"; }
}

interface ReportTarget {
    String fetch();
}

public class ReportAdapter implements ReportTarget {
    private final ReportLegacyApi legacy;

    public ReportAdapter(ReportLegacyApi legacy) {
        this.legacy = legacy;
    }

    public String fetch() {
        String raw = legacy.legacyFetch();
        return raw.toLowerCase().replace("legacy-", "modern-");
    }
}
