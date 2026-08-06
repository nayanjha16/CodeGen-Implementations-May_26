package org.example.patterns;
public class TicketFactoryTest {
    public static void main(String[] args) {
        TicketFactory f = new TicketFactory();
        if (!f.create("basic").operate().equals("basic-ticket")) throw new AssertionError();
        if (!f.create("premium").operate().equals("premium-ticket")) throw new AssertionError();
        System.out.println("ok");
    }
}
