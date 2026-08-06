// DesignPatternsSolid | kind=combo | label=adapter+isp | domain=cache | tier=errors
package org.example.patterns;

class CacheLegacyApi {
    public String legacyFetch() { return "LEGACY-cache"; }
}

interface CacheTarget {
    String fetch();
}

public class CacheAdapter implements CacheTarget {
    private final CacheLegacyApi legacy;

    public CacheAdapter(CacheLegacyApi legacy) {
        this.legacy = legacy;
    }

    public String fetch() {
        String raw = legacy.legacyFetch();
        return raw.toLowerCase().replace("legacy-", "modern-");
    }
}
