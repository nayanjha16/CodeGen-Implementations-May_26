// DesignPatternsSolid | kind=design_pattern | label=visitor | domain=backup | tier=logging
package org.example.patterns;

interface BackupVisitor {
    String visitLeaf(BackupLeaf leaf);
}

interface BackupElement {
    String accept(BackupVisitor v);
}

class BackupLeaf implements BackupElement {
    final String name;
    public BackupLeaf(String name) { this.name = name; }
    public String accept(BackupVisitor v) { return v.visitLeaf(this); }
}

public class BackupPrintVisitor implements BackupVisitor {
    public String visitLeaf(BackupLeaf leaf) { return "backup:" + leaf.name; }
}
