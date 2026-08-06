package org.example.patterns;
public class ShippingLspTest {
    public static void main(String[] args) {
        ShippingShape[] arr = new ShippingShape[] { new ShippingRectangle(2,3), new ShippingSquare(4) };
        if (ShippingLspUtil.total(arr) != 22) throw new AssertionError();
        System.out.println("ok");
    }
}
