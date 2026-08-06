// DesignPatternsSolid | kind=design_pattern | label=visitor | domain=game | tier=errors
package org.example.patterns;

interface GameVisitor {
    String visitLeaf(GameLeaf leaf);
}

interface GameElement {
    String accept(GameVisitor v);
}

class GameLeaf implements GameElement {
    final String name;
    public GameLeaf(String name) { this.name = name; }
    public String accept(GameVisitor v) { return v.visitLeaf(this); }
}

public class GamePrintVisitor implements GameVisitor {
    public String visitLeaf(GameLeaf leaf) { return "game:" + leaf.name; }
}
