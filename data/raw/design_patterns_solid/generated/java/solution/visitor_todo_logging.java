// DesignPatternsSolid | kind=design_pattern | label=visitor | domain=todo | tier=logging
package org.example.patterns;

interface TodoVisitor {
    String visitLeaf(TodoLeaf leaf);
}

interface TodoElement {
    String accept(TodoVisitor v);
}

class TodoLeaf implements TodoElement {
    final String name;
    public TodoLeaf(String name) { this.name = name; }
    public String accept(TodoVisitor v) { return v.visitLeaf(this); }
}

public class TodoPrintVisitor implements TodoVisitor {
    public String visitLeaf(TodoLeaf leaf) { return "todo:" + leaf.name; }
}
