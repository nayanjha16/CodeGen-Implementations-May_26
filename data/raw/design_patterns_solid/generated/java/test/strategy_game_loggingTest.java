package org.example.patterns;
public class GameStrategyTest {
    public static void main(String[] args) {
        GameContext ctx = new GameContext(new GameDiscountStrategy());
        if (ctx.execute(10) != 5) throw new AssertionError();
        System.out.println("ok");
    }
}
