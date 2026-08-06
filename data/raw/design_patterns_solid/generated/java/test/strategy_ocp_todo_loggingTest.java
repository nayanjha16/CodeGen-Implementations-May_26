package org.example.patterns;
public class TodoStrategyTest {
    public static void main(String[] args) {
        TodoContext ctx = new TodoContext(new TodoDiscountStrategy());
        if (ctx.execute(10) != 5) throw new AssertionError();
        System.out.println("ok");
    }
}
