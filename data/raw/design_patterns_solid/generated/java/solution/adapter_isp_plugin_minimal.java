// DesignPatternsSolid | kind=combo | label=adapter+isp | domain=plugin | tier=minimal
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
