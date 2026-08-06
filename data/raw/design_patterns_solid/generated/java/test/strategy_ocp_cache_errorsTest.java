package org.example.patterns;
public class CacheStrategyTest {
    public static void main(String[] args) {
        CacheContext ctx = new CacheContext(new CacheDiscountStrategy());
        if (ctx.execute(10) != 5) throw new AssertionError();
        System.out.println("ok");
    }
}
