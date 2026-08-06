// DesignPatternsSolid | kind=combo | label=adapter+isp | domain=storage | tier=minimal
package org.example.patterns;

class StorageLegacyApi {
    public String legacyFetch() { return "LEGACY-storage"; }
}

interface StorageTarget {
    String fetch();
}

public class StorageAdapter implements StorageTarget {
    private final StorageLegacyApi legacy;

    public StorageAdapter(StorageLegacyApi legacy) {
        this.legacy = legacy;
    }

    public String fetch() {
        String raw = legacy.legacyFetch();
        return raw.toLowerCase().replace("legacy-", "modern-");
    }
}
