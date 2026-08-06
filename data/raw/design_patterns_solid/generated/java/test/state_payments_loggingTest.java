package org.example.patterns;
public class PaymentsStateTest {
    public static void main(String[] args) {
        PaymentsContext ctx = new PaymentsContext();
        if (!ctx.request().equals("was-off-payments")) throw new AssertionError();
        if (!ctx.request().equals("was-on-payments")) throw new AssertionError();
        System.out.println("ok");
    }
}
