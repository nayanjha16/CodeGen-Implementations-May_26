// DesignPatternsSolid | kind=design_pattern | label=factory | domain=review | tier=minimal
package org.example.patterns;

interface ReviewProduct {
    String operate();
}

class ReviewBasicProduct implements ReviewProduct {
    public String operate() { return "basic-review"; }
}

class ReviewPremiumProduct implements ReviewProduct {
    public String operate() { return "premium-review"; }
}

public class ReviewFactory {
    public ReviewProduct create(String type) {
        if ("premium".equalsIgnoreCase(type)) return new ReviewPremiumProduct();
        return new ReviewBasicProduct();
    }
}
