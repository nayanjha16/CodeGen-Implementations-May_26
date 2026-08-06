package org.example.patterns;
public class BookingVisitorTest {
    public static void main(String[] args) {
        String out = new BookingLeaf("n").accept(new BookingPrintVisitor());
        if (!out.equals("booking:n")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
