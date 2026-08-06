// DesignPatternsSolid | kind=combo | label=factory+dip | domain=comment | tier=minimal
package org.example.patterns;

interface CommentProduct {
    String operate();
}

class CommentBasicProduct implements CommentProduct {
    public String operate() { return "basic-comment"; }
}

class CommentPremiumProduct implements CommentProduct {
    public String operate() { return "premium-comment"; }
}

public class CommentFactory {
    public CommentProduct create(String type) {
        if ("premium".equalsIgnoreCase(type)) return new CommentPremiumProduct();
        return new CommentBasicProduct();
    }
}
