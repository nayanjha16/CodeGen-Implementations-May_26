package org.example.patterns;
public class CartStateTest {
    public static void main(String[] args) {
        CartContext ctx = new CartContext();
        if (!ctx.request().equals("was-off-cart")) throw new AssertionError();
        if (!ctx.request().equals("was-on-cart")) throw new AssertionError();
        System.out.println("ok");
    }
}
