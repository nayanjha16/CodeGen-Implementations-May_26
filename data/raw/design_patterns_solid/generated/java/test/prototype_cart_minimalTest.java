package org.example.patterns;
public class CartPrototypeTest {
    public static void main(String[] args) {
        CartPrototype a = new CartPrototype("cart", 2);
        CartPrototype b = a.copy();
        b.setLabel("cart-copy");
        if (a.describe().equals(b.describe())) throw new AssertionError();
        System.out.println("ok");
    }
}
