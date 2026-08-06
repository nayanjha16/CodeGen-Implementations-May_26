// DesignPatternsSolid | kind=design_pattern | label=visitor | domain=booking | tier=logging
package org.example.patterns;

interface BookingVisitor {
    String visitLeaf(BookingLeaf leaf);
}

interface BookingElement {
    String accept(BookingVisitor v);
}

class BookingLeaf implements BookingElement {
    final String name;
    public BookingLeaf(String name) { this.name = name; }
    public String accept(BookingVisitor v) { return v.visitLeaf(this); }
}

public class BookingPrintVisitor implements BookingVisitor {
    public String visitLeaf(BookingLeaf leaf) { return "booking:" + leaf.name; }
}
