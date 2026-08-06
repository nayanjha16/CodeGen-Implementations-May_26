// DesignPatternsSolid | kind=design_pattern | label=visitor | domain=storage | tier=minimal
package org.example.patterns;

interface StorageVisitor {
    String visitLeaf(StorageLeaf leaf);
}

interface StorageElement {
    String accept(StorageVisitor v);
}

class StorageLeaf implements StorageElement {
    final String name;
    public StorageLeaf(String name) { this.name = name; }
    public String accept(StorageVisitor v) { return v.visitLeaf(this); }
}

public class StoragePrintVisitor implements StorageVisitor {
    public String visitLeaf(StorageLeaf leaf) { return "storage:" + leaf.name; }
}
