package org.example.patterns;
public class InventoryStrategyTest {
    public static void main(String[] args) {
        InventoryContext ctx = new InventoryContext(new InventoryDiscountStrategy());
        if (ctx.execute(10) != 5) throw new AssertionError();
        System.out.println("ok");
    }
}
