package org.example.patterns;
public class AudioStrategyTest {
    public static void main(String[] args) {
        AudioContext ctx = new AudioContext(new AudioDiscountStrategy());
        if (ctx.execute(10) != 5) throw new AssertionError();
        System.out.println("ok");
    }
}
