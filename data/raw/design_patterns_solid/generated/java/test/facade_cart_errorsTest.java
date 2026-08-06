package org.example.patterns;
public class CartFacadeTest {
    public static void main(String[] args) {
        CartFacade f = new CartFacade();
        if (!f.submit("x").equals("wrote-cart:x")) throw new AssertionError();
        System.out.println("ok");
    }
}
