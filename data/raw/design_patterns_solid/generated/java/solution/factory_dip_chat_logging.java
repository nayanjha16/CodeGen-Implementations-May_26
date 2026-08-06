// DesignPatternsSolid | kind=combo | label=factory+dip | domain=chat | tier=logging
package org.example.patterns;

interface ChatProduct {
    String operate();
}

class ChatBasicProduct implements ChatProduct {
    public String operate() { return "basic-chat"; }
}

class ChatPremiumProduct implements ChatProduct {
    public String operate() { return "premium-chat"; }
}

public class ChatFactory {
    public ChatProduct create(String type) {
        System.out.println("[log] create " + type);
        if ("premium".equalsIgnoreCase(type)) return new ChatPremiumProduct();
        return new ChatBasicProduct();
    }
}
