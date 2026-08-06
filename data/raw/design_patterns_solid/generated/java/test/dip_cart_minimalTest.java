package org.example.patterns;
public class CartDipTest {
    public static void main(String[] args) {
        String out = new CartAppService(new CartHttpGateway()).publish("p");
        if (!out.equals("http-cart:p")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
