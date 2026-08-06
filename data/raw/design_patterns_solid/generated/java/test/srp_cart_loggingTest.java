package org.example.patterns;
public class CartSrpTest {
    public static void main(String[] args) {
        CartRecord r = new CartRecord("a", 3);
        if (!new CartFormatter().format(r).equals("a=3")) throw new AssertionError();
        System.out.println("ok");
    }
}
