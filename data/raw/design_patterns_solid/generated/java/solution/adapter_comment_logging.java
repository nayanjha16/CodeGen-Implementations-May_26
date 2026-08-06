// DesignPatternsSolid | kind=design_pattern | label=adapter | domain=comment | tier=logging
package org.example.patterns;

class CommentLegacyApi {
    public String legacyFetch() { return "LEGACY-comment"; }
}

interface CommentTarget {
    String fetch();
}

public class CommentAdapter implements CommentTarget {
    private final CommentLegacyApi legacy;

    public CommentAdapter(CommentLegacyApi legacy) {
        this.legacy = legacy;
    }

    public String fetch() {
        String raw = legacy.legacyFetch();
        return raw.toLowerCase().replace("legacy-", "modern-");
    }
}
