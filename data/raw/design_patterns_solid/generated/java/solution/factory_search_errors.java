// DesignPatternsSolid | kind=design_pattern | label=factory | domain=search | tier=errors
package org.example.patterns;

interface SearchProduct {
    String operate();
}

class SearchBasicProduct implements SearchProduct {
    public String operate() { return "basic-search"; }
}

class SearchPremiumProduct implements SearchProduct {
    public String operate() { return "premium-search"; }
}

public class SearchFactory {
    public SearchProduct create(String type) {
        if (type == null || type.isEmpty()) throw new IllegalArgumentException("type required");
        System.out.println("[log] create " + type);
        if ("premium".equalsIgnoreCase(type)) return new SearchPremiumProduct();
        return new SearchBasicProduct();
    }
}
