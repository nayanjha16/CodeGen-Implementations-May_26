package org.example.patterns;
public class CartTemplateTest {
    public static void main(String[] args) {
        String out = new CartUpperTemplate().run(" ab ");
        if (!out.equals("cart|AB")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
