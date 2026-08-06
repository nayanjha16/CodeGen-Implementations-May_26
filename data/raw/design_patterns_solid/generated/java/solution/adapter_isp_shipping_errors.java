// DesignPatternsSolid | kind=combo | label=adapter+isp | domain=shipping | tier=errors
package org.example.patterns;

class ShippingLegacyApi {
    public String legacyFetch() { return "LEGACY-shipping"; }
}

interface ShippingTarget {
    String fetch();
}

public class ShippingAdapter implements ShippingTarget {
    private final ShippingLegacyApi legacy;

    public ShippingAdapter(ShippingLegacyApi legacy) {
        this.legacy = legacy;
    }

    public String fetch() {
        String raw = legacy.legacyFetch();
        return raw.toLowerCase().replace("legacy-", "modern-");
    }
}
