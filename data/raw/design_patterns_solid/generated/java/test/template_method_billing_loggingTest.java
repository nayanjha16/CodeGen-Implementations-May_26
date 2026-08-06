package org.example.patterns;
public class BillingTemplateTest {
    public static void main(String[] args) {
        String out = new BillingUpperTemplate().run(" ab ");
        if (!out.equals("billing|AB")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
