// DesignPatternsSolid | kind=design_pattern | label=adapter | domain=todo | tier=errors
package org.example.patterns;

class TodoLegacyApi {
    public String legacyFetch() { return "LEGACY-todo"; }
}

interface TodoTarget {
    String fetch();
}

public class TodoAdapter implements TodoTarget {
    private final TodoLegacyApi legacy;

    public TodoAdapter(TodoLegacyApi legacy) {
        this.legacy = legacy;
    }

    public String fetch() {
        String raw = legacy.legacyFetch();
        return raw.toLowerCase().replace("legacy-", "modern-");
    }
}
