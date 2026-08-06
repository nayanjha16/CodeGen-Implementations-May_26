// DesignPatternsSolid | kind=combo | label=adapter+isp | domain=auth | tier=errors
package org.example.patterns;

class AuthLegacyApi {
    public String legacyFetch() { return "LEGACY-auth"; }
}

interface AuthTarget {
    String fetch();
}

public class AuthAdapter implements AuthTarget {
    private final AuthLegacyApi legacy;

    public AuthAdapter(AuthLegacyApi legacy) {
        this.legacy = legacy;
    }

    public String fetch() {
        String raw = legacy.legacyFetch();
        return raw.toLowerCase().replace("legacy-", "modern-");
    }
}
