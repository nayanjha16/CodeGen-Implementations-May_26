// DesignPatternsSolid | kind=combo | label=adapter+isp | domain=streaming | tier=errors
package org.example.patterns;

class StreamingLegacyApi {
    public String legacyFetch() { return "LEGACY-streaming"; }
}

interface StreamingTarget {
    String fetch();
}

public class StreamingAdapter implements StreamingTarget {
    private final StreamingLegacyApi legacy;

    public StreamingAdapter(StreamingLegacyApi legacy) {
        this.legacy = legacy;
    }

    public String fetch() {
        String raw = legacy.legacyFetch();
        return raw.toLowerCase().replace("legacy-", "modern-");
    }
}
