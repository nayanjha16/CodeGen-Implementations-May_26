package org.example.patterns;
public class DiscountLspTest {
    public static void main(String[] args) {
        DiscountShape[] arr = new DiscountShape[] { new DiscountRectangle(2,3), new DiscountSquare(4) };
        if (DiscountLspUtil.total(arr) != 22) throw new AssertionError();
        System.out.println("ok");
    }
}
