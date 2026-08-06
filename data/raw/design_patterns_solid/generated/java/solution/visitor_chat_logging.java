// DesignPatternsSolid | kind=design_pattern | label=visitor | domain=chat | tier=logging
package org.example.patterns;

interface ChatVisitor {
    String visitLeaf(ChatLeaf leaf);
}

interface ChatElement {
    String accept(ChatVisitor v);
}

class ChatLeaf implements ChatElement {
    final String name;
    public ChatLeaf(String name) { this.name = name; }
    public String accept(ChatVisitor v) { return v.visitLeaf(this); }
}

public class ChatPrintVisitor implements ChatVisitor {
    public String visitLeaf(ChatLeaf leaf) { return "chat:" + leaf.name; }
}
