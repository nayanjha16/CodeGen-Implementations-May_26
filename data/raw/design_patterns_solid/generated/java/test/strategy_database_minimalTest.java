package org.example.patterns;
public class DatabaseStrategyTest {
    public static void main(String[] args) {
        DatabaseContext ctx = new DatabaseContext(new DatabaseDiscountStrategy());
        if (ctx.execute(10) != 5) throw new AssertionError();
        System.out.println("ok");
    }
}
