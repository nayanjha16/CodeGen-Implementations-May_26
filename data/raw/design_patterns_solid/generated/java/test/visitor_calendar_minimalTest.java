package org.example.patterns;
public class CalendarVisitorTest {
    public static void main(String[] args) {
        String out = new CalendarLeaf("n").accept(new CalendarPrintVisitor());
        if (!out.equals("calendar:n")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
