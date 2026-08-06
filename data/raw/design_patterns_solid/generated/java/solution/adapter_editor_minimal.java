// DesignPatternsSolid | kind=design_pattern | label=adapter | domain=editor | tier=minimal
package org.example.patterns;

class EditorLegacyApi {
    public String legacyFetch() { return "LEGACY-editor"; }
}

interface EditorTarget {
    String fetch();
}

public class EditorAdapter implements EditorTarget {
    private final EditorLegacyApi legacy;

    public EditorAdapter(EditorLegacyApi legacy) {
        this.legacy = legacy;
    }

    public String fetch() {
        String raw = legacy.legacyFetch();
        return raw.toLowerCase().replace("legacy-", "modern-");
    }
}
