package org.example.patterns;
public class TicketSrpTest {
    public static void main(String[] args) {
        TicketRecord r = new TicketRecord("a", 3);
        if (!new TicketFormatter().format(r).equals("a=3")) throw new AssertionError();
        System.out.println("ok");
    }
}
