// DesignPatternsSolid | kind=combo | label=adapter+isp | domain=cart | tier=logging
package org.example.patterns;

class CartLegacyApi {
    public String legacyFetch() { return "LEGACY-cart"; }
}

interface CartTarget {
    String fetch();
}

public class CartAdapter implements CartTarget {
    private final CartLegacyApi legacy;

    public CartAdapter(CartLegacyApi legacy) {
        this.legacy = legacy;
    }

    public String fetch() {
        String raw = legacy.legacyFetch();
        return raw.toLowerCase().replace("legacy-", "modern-");
    }
}
