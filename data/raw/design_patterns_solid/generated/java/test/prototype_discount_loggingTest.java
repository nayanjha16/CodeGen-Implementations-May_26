package org.example.patterns;
public class DiscountPrototypeTest {
    public static void main(String[] args) {
        DiscountPrototype a = new DiscountPrototype("discount", 2);
        DiscountPrototype b = a.copy();
        b.setLabel("discount-copy");
        if (a.describe().equals(b.describe())) throw new AssertionError();
        System.out.println("ok");
    }
}
