// DesignPatternsSolid | kind=combo | label=factory+dip | domain=feed | tier=logging
package org.example.patterns;

interface FeedProduct {
    String operate();
}

class FeedBasicProduct implements FeedProduct {
    public String operate() { return "basic-feed"; }
}

class FeedPremiumProduct implements FeedProduct {
    public String operate() { return "premium-feed"; }
}

public class FeedFactory {
    public FeedProduct create(String type) {
        System.out.println("[log] create " + type);
        if ("premium".equalsIgnoreCase(type)) return new FeedPremiumProduct();
        return new FeedBasicProduct();
    }
}
