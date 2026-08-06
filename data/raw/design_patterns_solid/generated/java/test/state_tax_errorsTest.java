package org.example.patterns;
public class TaxStateTest {
    public static void main(String[] args) {
        TaxContext ctx = new TaxContext();
        if (!ctx.request().equals("was-off-tax")) throw new AssertionError();
        if (!ctx.request().equals("was-on-tax")) throw new AssertionError();
        System.out.println("ok");
    }
}
