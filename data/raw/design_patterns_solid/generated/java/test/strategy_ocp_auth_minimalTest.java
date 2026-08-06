package org.example.patterns;
public class AuthStrategyTest {
    public static void main(String[] args) {
        AuthContext ctx = new AuthContext(new AuthDiscountStrategy());
        if (ctx.execute(10) != 5) throw new AssertionError();
        System.out.println("ok");
    }
}
