package org.example.patterns;
public class TicketAdapterTest {
    public static void main(String[] args) {
        TicketTarget t = new TicketAdapter(new TicketLegacyApi());
        if (!t.fetch().equals("modern-ticket")) throw new AssertionError(t.fetch());
        System.out.println("ok");
    }
}
