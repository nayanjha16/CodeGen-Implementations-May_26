package org.example.patterns;
public class TicketDecoratorTest {
    public static void main(String[] args) {
        TicketComponent c = new TicketUpperDecorator(new TicketCore());
        String out = c.process("ab");
        if (!out.equals("TICKET:AB")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
