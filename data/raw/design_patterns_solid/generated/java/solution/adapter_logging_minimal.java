// DesignPatternsSolid | kind=design_pattern | label=adapter | domain=logging | tier=minimal
package org.example.patterns;

class LoggingLegacyApi {
    public String legacyFetch() { return "LEGACY-logging"; }
}

interface LoggingTarget {
    String fetch();
}

public class LoggingAdapter implements LoggingTarget {
    private final LoggingLegacyApi legacy;

    public LoggingAdapter(LoggingLegacyApi legacy) {
        this.legacy = legacy;
    }

    public String fetch() {
        String raw = legacy.legacyFetch();
        return raw.toLowerCase().replace("legacy-", "modern-");
    }
}
