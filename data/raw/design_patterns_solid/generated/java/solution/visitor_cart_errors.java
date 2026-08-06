// DesignPatternsSolid | kind=design_pattern | label=visitor | domain=cart | tier=errors
package org.example.patterns;

interface CartVisitor {
    String visitLeaf(CartLeaf leaf);
}

interface CartElement {
    String accept(CartVisitor v);
}

class CartLeaf implements CartElement {
    final String name;
    public CartLeaf(String name) { this.name = name; }
    public String accept(CartVisitor v) { return v.visitLeaf(this); }
}

public class CartPrintVisitor implements CartVisitor {
    public String visitLeaf(CartLeaf leaf) { return "cart:" + leaf.name; }
}
