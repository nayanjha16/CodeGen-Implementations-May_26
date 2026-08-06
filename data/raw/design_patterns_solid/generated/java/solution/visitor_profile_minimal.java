// DesignPatternsSolid | kind=design_pattern | label=visitor | domain=profile | tier=minimal
package org.example.patterns;

interface ProfileVisitor {
    String visitLeaf(ProfileLeaf leaf);
}

interface ProfileElement {
    String accept(ProfileVisitor v);
}

class ProfileLeaf implements ProfileElement {
    final String name;
    public ProfileLeaf(String name) { this.name = name; }
    public String accept(ProfileVisitor v) { return v.visitLeaf(this); }
}

public class ProfilePrintVisitor implements ProfileVisitor {
    public String visitLeaf(ProfileLeaf leaf) { return "profile:" + leaf.name; }
}
