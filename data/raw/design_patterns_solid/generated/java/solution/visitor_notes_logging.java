// DesignPatternsSolid | kind=design_pattern | label=visitor | domain=notes | tier=logging
package org.example.patterns;

interface NotesVisitor {
    String visitLeaf(NotesLeaf leaf);
}

interface NotesElement {
    String accept(NotesVisitor v);
}

class NotesLeaf implements NotesElement {
    final String name;
    public NotesLeaf(String name) { this.name = name; }
    public String accept(NotesVisitor v) { return v.visitLeaf(this); }
}

public class NotesPrintVisitor implements NotesVisitor {
    public String visitLeaf(NotesLeaf leaf) { return "notes:" + leaf.name; }
}
