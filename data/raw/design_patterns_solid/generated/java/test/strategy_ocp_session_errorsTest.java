package org.example.patterns;
public class SessionStrategyTest {
    public static void main(String[] args) {
        SessionContext ctx = new SessionContext(new SessionDiscountStrategy());
        if (ctx.execute(10) != 5) throw new AssertionError();
        System.out.println("ok");
    }
}
