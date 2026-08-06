// DesignPatternsSolid | kind=design_pattern | label=adapter | domain=plugin | tier=logging
package org.example.patterns;

class PluginLegacyApi {
    public String legacyFetch() { return "LEGACY-plugin"; }
}

interface PluginTarget {
    String fetch();
}

public class PluginAdapter implements PluginTarget {
    private final PluginLegacyApi legacy;

    public PluginAdapter(PluginLegacyApi legacy) {
        this.legacy = legacy;
    }

    public String fetch() {
        String raw = legacy.legacyFetch();
        return raw.toLowerCase().replace("legacy-", "modern-");
    }
}
