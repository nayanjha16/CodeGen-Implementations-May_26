// DesignPatternsSolid | kind=combo | label=adapter+isp | domain=video | tier=errors
package org.example.patterns;

class VideoLegacyApi {
    public String legacyFetch() { return "LEGACY-video"; }
}

interface VideoTarget {
    String fetch();
}

public class VideoAdapter implements VideoTarget {
    private final VideoLegacyApi legacy;

    public VideoAdapter(VideoLegacyApi legacy) {
        this.legacy = legacy;
    }

    public String fetch() {
        String raw = legacy.legacyFetch();
        return raw.toLowerCase().replace("legacy-", "modern-");
    }
}
