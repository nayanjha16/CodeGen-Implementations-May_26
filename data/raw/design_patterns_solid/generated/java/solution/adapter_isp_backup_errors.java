// DesignPatternsSolid | kind=combo | label=adapter+isp | domain=backup | tier=errors
package org.example.patterns;

class BackupLegacyApi {
    public String legacyFetch() { return "LEGACY-backup"; }
}

interface BackupTarget {
    String fetch();
}

public class BackupAdapter implements BackupTarget {
    private final BackupLegacyApi legacy;

    public BackupAdapter(BackupLegacyApi legacy) {
        this.legacy = legacy;
    }

    public String fetch() {
        String raw = legacy.legacyFetch();
        return raw.toLowerCase().replace("legacy-", "modern-");
    }
}
