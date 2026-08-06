package org.example.patterns;
public class TicketOcpTest {
    public static void main(String[] args) {
        if (new TicketPriceEngine(new TicketTenPercent()).quote(100) != 90) throw new AssertionError();
        System.out.println("ok");
    }
}
