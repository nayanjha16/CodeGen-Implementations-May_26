// DesignPatternsSolid | kind=combo | label=adapter+isp | domain=game | tier=minimal
package org.example.patterns;

class GameLegacyApi {
    public String legacyFetch() { return "LEGACY-game"; }
}

interface GameTarget {
    String fetch();
}

public class GameAdapter implements GameTarget {
    private final GameLegacyApi legacy;

    public GameAdapter(GameLegacyApi legacy) {
        this.legacy = legacy;
    }

    public String fetch() {
        String raw = legacy.legacyFetch();
        return raw.toLowerCase().replace("legacy-", "modern-");
    }
}
