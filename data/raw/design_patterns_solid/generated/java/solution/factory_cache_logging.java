// DesignPatternsSolid | kind=design_pattern | label=factory | domain=cache | tier=logging
package org.example.patterns;

interface CacheProduct {
    String operate();
}

class CacheBasicProduct implements CacheProduct {
    public String operate() { return "basic-cache"; }
}

class CachePremiumProduct implements CacheProduct {
    public String operate() { return "premium-cache"; }
}

public class CacheFactory {
    public CacheProduct create(String type) {
        System.out.println("[log] create " + type);
        if ("premium".equalsIgnoreCase(type)) return new CachePremiumProduct();
        return new CacheBasicProduct();
    }
}
