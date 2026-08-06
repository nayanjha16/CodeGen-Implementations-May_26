// DesignPatternsSolid | kind=design_pattern | label=adapter | domain=audio | tier=errors
package org.example.patterns;

class AudioLegacyApi {
    public String legacyFetch() { return "LEGACY-audio"; }
}

interface AudioTarget {
    String fetch();
}

public class AudioAdapter implements AudioTarget {
    private final AudioLegacyApi legacy;

    public AudioAdapter(AudioLegacyApi legacy) {
        this.legacy = legacy;
    }

    public String fetch() {
        String raw = legacy.legacyFetch();
        return raw.toLowerCase().replace("legacy-", "modern-");
    }
}
