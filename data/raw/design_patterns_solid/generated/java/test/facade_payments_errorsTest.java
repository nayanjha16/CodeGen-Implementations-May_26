package org.example.patterns;
public class PaymentsFacadeTest {
    public static void main(String[] args) {
        PaymentsFacade f = new PaymentsFacade();
        if (!f.submit("x").equals("wrote-payments:x")) throw new AssertionError();
        System.out.println("ok");
    }
}
