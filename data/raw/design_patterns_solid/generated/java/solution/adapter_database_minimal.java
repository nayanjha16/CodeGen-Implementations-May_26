// DesignPatternsSolid | kind=design_pattern | label=adapter | domain=database | tier=minimal
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
