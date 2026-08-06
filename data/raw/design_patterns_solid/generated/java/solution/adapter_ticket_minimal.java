// DesignPatternsSolid | kind=design_pattern | label=adapter | domain=ticket | tier=minimal
package org.example.patterns;

class TicketLegacyApi {
    public String legacyFetch() { return "LEGACY-ticket"; }
}

interface TicketTarget {
    String fetch();
}

public class TicketAdapter implements TicketTarget {
    private final TicketLegacyApi legacy;

    public TicketAdapter(TicketLegacyApi legacy) {
        this.legacy = legacy;
    }

    public String fetch() {
        String raw = legacy.legacyFetch();
        return raw.toLowerCase().replace("legacy-", "modern-");
    }
}
