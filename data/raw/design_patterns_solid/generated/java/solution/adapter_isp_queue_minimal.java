// DesignPatternsSolid | kind=combo | label=adapter+isp | domain=queue | tier=minimal
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
