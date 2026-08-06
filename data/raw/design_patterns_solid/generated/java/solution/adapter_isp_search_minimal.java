// DesignPatternsSolid | kind=combo | label=adapter+isp | domain=search | tier=minimal
package org.example.patterns;

class SearchLegacyApi {
    public String legacyFetch() { return "LEGACY-search"; }
}

interface SearchTarget {
    String fetch();
}

public class SearchAdapter implements SearchTarget {
    private final SearchLegacyApi legacy;

    public SearchAdapter(SearchLegacyApi legacy) {
        this.legacy = legacy;
    }

    public String fetch() {
        String raw = legacy.legacyFetch();
        return raw.toLowerCase().replace("legacy-", "modern-");
    }
}
