// DesignPatternsSolid | kind=combo | label=adapter+isp | domain=chat | tier=minimal
package org.example.patterns;

class ChatLegacyApi {
    public String legacyFetch() { return "LEGACY-chat"; }
}

interface ChatTarget {
    String fetch();
}

public class ChatAdapter implements ChatTarget {
    private final ChatLegacyApi legacy;

    public ChatAdapter(ChatLegacyApi legacy) {
        this.legacy = legacy;
    }

    public String fetch() {
        String raw = legacy.legacyFetch();
        return raw.toLowerCase().replace("legacy-", "modern-");
    }
}
