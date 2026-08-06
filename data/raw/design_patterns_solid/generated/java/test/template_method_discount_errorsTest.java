package org.example.patterns;
public class DiscountTemplateTest {
    public static void main(String[] args) {
        String out = new DiscountUpperTemplate().run(" ab ");
        if (!out.equals("discount|AB")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
