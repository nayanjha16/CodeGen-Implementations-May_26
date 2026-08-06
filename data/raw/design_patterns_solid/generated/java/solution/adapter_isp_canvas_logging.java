// DesignPatternsSolid | kind=combo | label=adapter+isp | domain=canvas | tier=logging
package org.example.patterns;

class CanvasLegacyApi {
    public String legacyFetch() { return "LEGACY-canvas"; }
}

interface CanvasTarget {
    String fetch();
}

public class CanvasAdapter implements CanvasTarget {
    private final CanvasLegacyApi legacy;

    public CanvasAdapter(CanvasLegacyApi legacy) {
        this.legacy = legacy;
    }

    public String fetch() {
        String raw = legacy.legacyFetch();
        return raw.toLowerCase().replace("legacy-", "modern-");
    }
}
