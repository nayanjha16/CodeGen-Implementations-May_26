// DesignPatternsSolid | kind=design_pattern | label=visitor | domain=calendar | tier=minimal
package org.example.patterns;

interface CalendarVisitor {
    String visitLeaf(CalendarLeaf leaf);
}

interface CalendarElement {
    String accept(CalendarVisitor v);
}

class CalendarLeaf implements CalendarElement {
    final String name;
    public CalendarLeaf(String name) { this.name = name; }
    public String accept(CalendarVisitor v) { return v.visitLeaf(this); }
}

public class CalendarPrintVisitor implements CalendarVisitor {
    public String visitLeaf(CalendarLeaf leaf) { return "calendar:" + leaf.name; }
}
