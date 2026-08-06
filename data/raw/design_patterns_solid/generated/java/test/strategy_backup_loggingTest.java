package org.example.patterns;
public class BackupStrategyTest {
    public static void main(String[] args) {
        BackupContext ctx = new BackupContext(new BackupDiscountStrategy());
        if (ctx.execute(10) != 5) throw new AssertionError();
        System.out.println("ok");
    }
}
