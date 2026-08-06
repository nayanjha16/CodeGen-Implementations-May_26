// DesignPatternsSolid | kind=design_pattern | label=visitor | domain=logging | tier=logging
package org.example.patterns;

interface LoggingVisitor {
    String visitLeaf(LoggingLeaf leaf);
}

interface LoggingElement {
    String accept(LoggingVisitor v);
}

class LoggingLeaf implements LoggingElement {
    final String name;
    public LoggingLeaf(String name) { this.name = name; }
    public String accept(LoggingVisitor v) { return v.visitLeaf(this); }
}

public class LoggingPrintVisitor implements LoggingVisitor {
    public String visitLeaf(LoggingLeaf leaf) { return "logging:" + leaf.name; }
}
