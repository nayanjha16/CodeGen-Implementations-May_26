package org.example.patterns;
public class CartOcpTest {
    public static void main(String[] args) {
        if (new CartPriceEngine(new CartTenPercent()).quote(100) != 90) throw new AssertionError();
        System.out.println("ok");
    }
}
