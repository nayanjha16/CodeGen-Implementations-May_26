// DesignPatternsSolid | kind=combo | label=adapter+isp | domain=notes | tier=errors
package org.example.patterns;

class NotesLegacyApi {
    public String legacyFetch() { return "LEGACY-notes"; }
}

interface NotesTarget {
    String fetch();
}

public class NotesAdapter implements NotesTarget {
    private final NotesLegacyApi legacy;

    public NotesAdapter(NotesLegacyApi legacy) {
        this.legacy = legacy;
    }

    public String fetch() {
        String raw = legacy.legacyFetch();
        return raw.toLowerCase().replace("legacy-", "modern-");
    }
}
