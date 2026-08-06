// DesignPatternsSolid | kind=design_pattern | label=factory | domain=chat | tier=errors
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
        if (type == null || type.isEmpty()) throw new IllegalArgumentException("type required");
        System.out.println("[log] create " + type);
        if ("premium".equalsIgnoreCase(type)) return new ChatPremiumProduct();
        return new ChatBasicProduct();
    }
}
