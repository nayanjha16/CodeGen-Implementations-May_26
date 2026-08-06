// DesignPatternsSolid | kind=design_pattern | label=adapter | domain=config | tier=minimal
package org.example.patterns;

class ConfigLegacyApi {
    public String legacyFetch() { return "LEGACY-config"; }
}

interface ConfigTarget {
    String fetch();
}

public class ConfigAdapter implements ConfigTarget {
    private final ConfigLegacyApi legacy;

    public ConfigAdapter(ConfigLegacyApi legacy) {
        this.legacy = legacy;
    }

    public String fetch() {
        String raw = legacy.legacyFetch();
        return raw.toLowerCase().replace("legacy-", "modern-");
    }
}
