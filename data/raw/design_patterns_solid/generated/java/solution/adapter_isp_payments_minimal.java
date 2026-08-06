// DesignPatternsSolid | kind=combo | label=adapter+isp | domain=payments | tier=minimal
package org.example.patterns;

class PaymentsLegacyApi {
    public String legacyFetch() { return "LEGACY-payments"; }
}

interface PaymentsTarget {
    String fetch();
}

public class PaymentsAdapter implements PaymentsTarget {
    private final PaymentsLegacyApi legacy;

    public PaymentsAdapter(PaymentsLegacyApi legacy) {
        this.legacy = legacy;
    }

    public String fetch() {
        String raw = legacy.legacyFetch();
        return raw.toLowerCase().replace("legacy-", "modern-");
    }
}
