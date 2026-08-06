// DesignPatternsSolid | kind=design_pattern | label=adapter | domain=queue | tier=logging
package org.example.patterns;

class QueueLegacyApi {
    public String legacyFetch() { return "LEGACY-queue"; }
}

interface QueueTarget {
    String fetch();
}

public class QueueAdapter implements QueueTarget {
    private final QueueLegacyApi legacy;

    public QueueAdapter(QueueLegacyApi legacy) {
        this.legacy = legacy;
    }

    public String fetch() {
        String raw = legacy.legacyFetch();
        return raw.toLowerCase().replace("legacy-", "modern-");
    }
}
