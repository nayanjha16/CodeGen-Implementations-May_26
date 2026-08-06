// DesignPatternsSolid | kind=design_pattern | label=visitor | domain=audio | tier=errors
package org.example.patterns;

interface AudioVisitor {
    String visitLeaf(AudioLeaf leaf);
}

interface AudioElement {
    String accept(AudioVisitor v);
}

class AudioLeaf implements AudioElement {
    final String name;
    public AudioLeaf(String name) { this.name = name; }
    public String accept(AudioVisitor v) { return v.visitLeaf(this); }
}

public class AudioPrintVisitor implements AudioVisitor {
    public String visitLeaf(AudioLeaf leaf) { return "audio:" + leaf.name; }
}
