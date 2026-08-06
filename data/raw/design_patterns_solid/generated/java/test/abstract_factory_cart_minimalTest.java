package org.example.patterns;
public class CartAbstractFactoryTest {
    public static void main(String[] args) {
        String out = CartAbstractFactoryDemo.run(new CartCloudFactory());
        if (!out.equals("cloud-btn-cart|cloud-dlg-cart")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
