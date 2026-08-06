package org.example.patterns;
public class CartLspTest {
    public static void main(String[] args) {
        CartShape[] arr = new CartShape[] { new CartRectangle(2,3), new CartSquare(4) };
        if (CartLspUtil.total(arr) != 22) throw new AssertionError();
        System.out.println("ok");
    }
}
