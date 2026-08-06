// DesignPatternsSolid | kind=design_pattern | label=adapter | domain=notifications | tier=minimal
package org.example.patterns;

class NotificationsLegacyApi {
    public String legacyFetch() { return "LEGACY-notifications"; }
}

interface NotificationsTarget {
    String fetch();
}

public class NotificationsAdapter implements NotificationsTarget {
    private final NotificationsLegacyApi legacy;

    public NotificationsAdapter(NotificationsLegacyApi legacy) {
        this.legacy = legacy;
    }

    public String fetch() {
        String raw = legacy.legacyFetch();
        return raw.toLowerCase().replace("legacy-", "modern-");
    }
}
