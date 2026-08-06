package org.example.patterns;
public class BookingCompositeTest {
    public static void main(String[] args) {
        BookingComposite root = new BookingComposite();
        root.add(new BookingLeaf(2));
        root.add(new BookingLeaf(3));
        if (root.size() != 5) throw new AssertionError();
        System.out.println("ok");
    }
}
