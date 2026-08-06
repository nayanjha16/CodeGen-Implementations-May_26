package org.example.patterns;
public class TicketDipTest {
    public static void main(String[] args) {
        String out = new TicketAppService(new TicketHttpGateway()).publish("p");
        if (!out.equals("http-ticket:p")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
