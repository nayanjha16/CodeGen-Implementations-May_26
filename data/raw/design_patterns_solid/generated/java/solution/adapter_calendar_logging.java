// DesignPatternsSolid | kind=design_pattern | label=adapter | domain=calendar | tier=logging
package org.example.patterns;

class CalendarLegacyApi {
    public String legacyFetch() { return "LEGACY-calendar"; }
}

interface CalendarTarget {
    String fetch();
}

public class CalendarAdapter implements CalendarTarget {
    private final CalendarLegacyApi legacy;

    public CalendarAdapter(CalendarLegacyApi legacy) {
        this.legacy = legacy;
    }

    public String fetch() {
        String raw = legacy.legacyFetch();
        return raw.toLowerCase().replace("legacy-", "modern-");
    }
}
