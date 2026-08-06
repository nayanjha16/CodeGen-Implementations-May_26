// DesignPatternsSolid | kind=design_pattern | label=adapter | domain=email | tier=minimal
package org.example.patterns;

class EmailLegacyApi {
    public String legacyFetch() { return "LEGACY-email"; }
}

interface EmailTarget {
    String fetch();
}

public class EmailAdapter implements EmailTarget {
    private final EmailLegacyApi legacy;

    public EmailAdapter(EmailLegacyApi legacy) {
        this.legacy = legacy;
    }

    public String fetch() {
        String raw = legacy.legacyFetch();
        return raw.toLowerCase().replace("legacy-", "modern-");
    }
}
