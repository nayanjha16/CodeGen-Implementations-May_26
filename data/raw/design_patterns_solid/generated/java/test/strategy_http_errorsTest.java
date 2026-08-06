package org.example.patterns;
public class HttpStrategyTest {
    public static void main(String[] args) {
        HttpContext ctx = new HttpContext(new HttpDiscountStrategy());
        if (ctx.execute(10) != 5) throw new AssertionError();
        System.out.println("ok");
    }
}
