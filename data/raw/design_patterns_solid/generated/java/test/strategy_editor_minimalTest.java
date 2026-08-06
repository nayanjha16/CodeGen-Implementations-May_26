package org.example.patterns;
public class EditorStrategyTest {
    public static void main(String[] args) {
        EditorContext ctx = new EditorContext(new EditorDiscountStrategy());
        if (ctx.execute(10) != 5) throw new AssertionError();
        System.out.println("ok");
    }
}
