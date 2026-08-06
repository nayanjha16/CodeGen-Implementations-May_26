package org.example.patterns;
public class CartStrategyTest {
    public static void main(String[] args) {
        CartContext ctx = new CartContext(new CartDiscountStrategy());
        if (ctx.execute(10) != 5) throw new AssertionError();
        System.out.println("ok");
    }
}
