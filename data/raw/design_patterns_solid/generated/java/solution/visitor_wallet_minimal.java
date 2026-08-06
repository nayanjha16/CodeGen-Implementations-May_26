// DesignPatternsSolid | kind=design_pattern | label=visitor | domain=wallet | tier=minimal
package org.example.patterns;

interface WalletVisitor {
    String visitLeaf(WalletLeaf leaf);
}

interface WalletElement {
    String accept(WalletVisitor v);
}

class WalletLeaf implements WalletElement {
    final String name;
    public WalletLeaf(String name) { this.name = name; }
    public String accept(WalletVisitor v) { return v.visitLeaf(this); }
}

public class WalletPrintVisitor implements WalletVisitor {
    public String visitLeaf(WalletLeaf leaf) { return "wallet:" + leaf.name; }
}
