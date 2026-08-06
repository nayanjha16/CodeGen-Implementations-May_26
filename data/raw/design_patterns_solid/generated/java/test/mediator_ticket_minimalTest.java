package org.example.patterns;
public class TicketMediatorTest {
    public static void main(String[] args) {
        TicketMediator m = new TicketMediator();
        new TicketColleague("a", m).send("hi");
        if (!m.history().equals("a->hi")) throw new AssertionError();
        System.out.println("ok");
    }
}
