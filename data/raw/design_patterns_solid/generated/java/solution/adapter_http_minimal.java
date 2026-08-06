// DesignPatternsSolid | kind=design_pattern | label=adapter | domain=http | tier=minimal
package org.example.patterns;

class HttpLegacyApi {
    public String legacyFetch() { return "LEGACY-http"; }
}

interface HttpTarget {
    String fetch();
}

public class HttpAdapter implements HttpTarget {
    private final HttpLegacyApi legacy;

    public HttpAdapter(HttpLegacyApi legacy) {
        this.legacy = legacy;
    }

    public String fetch() {
        String raw = legacy.legacyFetch();
        return raw.toLowerCase().replace("legacy-", "modern-");
    }
}
