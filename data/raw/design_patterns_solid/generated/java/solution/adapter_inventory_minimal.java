// DesignPatternsSolid | kind=design_pattern | label=adapter | domain=inventory | tier=minimal
package org.example.patterns;

class InventoryLegacyApi {
    public String legacyFetch() { return "LEGACY-inventory"; }
}

interface InventoryTarget {
    String fetch();
}

public class InventoryAdapter implements InventoryTarget {
    private final InventoryLegacyApi legacy;

    public InventoryAdapter(InventoryLegacyApi legacy) {
        this.legacy = legacy;
    }

    public String fetch() {
        String raw = legacy.legacyFetch();
        return raw.toLowerCase().replace("legacy-", "modern-");
    }
}
