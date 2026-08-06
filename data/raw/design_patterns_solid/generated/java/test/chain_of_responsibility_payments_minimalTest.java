package org.example.patterns;
public class PaymentsChainTest {
    public static void main(String[] args) {
        PaymentsHandler h = new PaymentsLowHandler();
        h.link(new PaymentsHighHandler());
        if (!h.handle(2, "m").equals("high-payments:m")) throw new AssertionError();
        System.out.println("ok");
    }
}
