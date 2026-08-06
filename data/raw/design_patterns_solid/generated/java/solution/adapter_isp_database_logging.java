// DesignPatternsSolid | kind=combo | label=adapter+isp | domain=database | tier=logging
package org.example.patterns;

class DatabaseLegacyApi {
    public String legacyFetch() { return "LEGACY-database"; }
}

interface DatabaseTarget {
    String fetch();
}

public class DatabaseAdapter implements DatabaseTarget {
    private final DatabaseLegacyApi legacy;

    public DatabaseAdapter(DatabaseLegacyApi legacy) {
        this.legacy = legacy;
    }

    public String fetch() {
        String raw = legacy.legacyFetch();
        return raw.toLowerCase().replace("legacy-", "modern-");
    }
}
