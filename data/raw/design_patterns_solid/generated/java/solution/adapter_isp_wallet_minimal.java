// DesignPatternsSolid | kind=combo | label=adapter+isp | domain=wallet | tier=minimal
package org.example.patterns;

class WalletLegacyApi {
    public String legacyFetch() { return "LEGACY-wallet"; }
}

interface WalletTarget {
    String fetch();
}

public class WalletAdapter implements WalletTarget {
    private final WalletLegacyApi legacy;

    public WalletAdapter(WalletLegacyApi legacy) {
        this.legacy = legacy;
    }

    public String fetch() {
        String raw = legacy.legacyFetch();
        return raw.toLowerCase().replace("legacy-", "modern-");
    }
}
