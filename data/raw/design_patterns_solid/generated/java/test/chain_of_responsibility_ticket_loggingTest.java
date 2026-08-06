package org.example.patterns;
public class TicketChainTest {
    public static void main(String[] args) {
        TicketHandler h = new TicketLowHandler();
        h.link(new TicketHighHandler());
        if (!h.handle(2, "m").equals("high-ticket:m")) throw new AssertionError();
        System.out.println("ok");
    }
}
