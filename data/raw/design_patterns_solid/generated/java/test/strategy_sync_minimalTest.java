package org.example.patterns;
public class SyncStrategyTest {
    public static void main(String[] args) {
        SyncContext ctx = new SyncContext(new SyncDiscountStrategy());
        if (ctx.execute(10) != 5) throw new AssertionError();
        System.out.println("ok");
    }
}
