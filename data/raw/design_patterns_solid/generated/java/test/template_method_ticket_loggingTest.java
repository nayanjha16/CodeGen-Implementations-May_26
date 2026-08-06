package org.example.patterns;
public class TicketTemplateTest {
    public static void main(String[] args) {
        String out = new TicketUpperTemplate().run(" ab ");
        if (!out.equals("ticket|AB")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
