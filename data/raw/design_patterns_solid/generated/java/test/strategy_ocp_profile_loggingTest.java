package org.example.patterns;
public class ProfileStrategyTest {
    public static void main(String[] args) {
        ProfileContext ctx = new ProfileContext(new ProfileDiscountStrategy());
        if (ctx.execute(10) != 5) throw new AssertionError();
        System.out.println("ok");
    }
}
