package org.example.patterns;
public class TicketCompositeTest {
    public static void main(String[] args) {
        TicketComposite root = new TicketComposite();
        root.add(new TicketLeaf(2));
        root.add(new TicketLeaf(3));
        if (root.size() != 5) throw new AssertionError();
        System.out.println("ok");
    }
}
