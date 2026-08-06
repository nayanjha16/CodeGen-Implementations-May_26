package org.example.patterns;
public class LicenseStrategyTest {
    public static void main(String[] args) {
        LicenseContext ctx = new LicenseContext(new LicenseDiscountStrategy());
        if (ctx.execute(10) != 5) throw new AssertionError();
        System.out.println("ok");
    }
}
