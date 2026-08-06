// DesignPatternsSolid | kind=combo | label=adapter+isp | domain=session | tier=errors
package org.example.patterns;

class SessionLegacyApi {
    public String legacyFetch() { return "LEGACY-session"; }
}

interface SessionTarget {
    String fetch();
}

public class SessionAdapter implements SessionTarget {
    private final SessionLegacyApi legacy;

    public SessionAdapter(SessionLegacyApi legacy) {
        this.legacy = legacy;
    }

    public String fetch() {
        String raw = legacy.legacyFetch();
        return raw.toLowerCase().replace("legacy-", "modern-");
    }
}
