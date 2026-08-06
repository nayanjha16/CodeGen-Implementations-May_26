// DesignPatternsSolid | kind=design_pattern | label=visitor | domain=video | tier=logging
package org.example.patterns;

interface VideoVisitor {
    String visitLeaf(VideoLeaf leaf);
}

interface VideoElement {
    String accept(VideoVisitor v);
}

class VideoLeaf implements VideoElement {
    final String name;
    public VideoLeaf(String name) { this.name = name; }
    public String accept(VideoVisitor v) { return v.visitLeaf(this); }
}

public class VideoPrintVisitor implements VideoVisitor {
    public String visitLeaf(VideoLeaf leaf) { return "video:" + leaf.name; }
}
