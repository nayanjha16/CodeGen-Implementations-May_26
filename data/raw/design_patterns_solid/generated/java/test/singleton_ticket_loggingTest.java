package org.example.patterns;
public class TicketSingletonTest {
    public static void main(String[] args) {
        TicketSingleton a = TicketSingleton.getInstance();
        TicketSingleton b = TicketSingleton.getInstance();
        a.setValue("ticket-one");
        if (a != b) throw new AssertionError("not singleton");
        if (!b.getValue().equals("ticket-one")) throw new AssertionError("state not shared");
        System.out.println("ok");
    }
}
