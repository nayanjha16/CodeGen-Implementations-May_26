// DesignPatternsSolid | kind=combo | label=factory+dip | domain=search | tier=minimal
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
        if ("premium".equalsIgnoreCase(type)) return new SearchPremiumProduct();
        return new SearchBasicProduct();
    }
}
