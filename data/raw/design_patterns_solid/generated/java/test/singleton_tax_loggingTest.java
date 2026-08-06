package org.example.patterns;
public class TaxSingletonTest {
    public static void main(String[] args) {
        TaxSingleton a = TaxSingleton.getInstance();
        TaxSingleton b = TaxSingleton.getInstance();
        a.setValue("tax-one");
        if (a != b) throw new AssertionError("not singleton");
        if (!b.getValue().equals("tax-one")) throw new AssertionError("state not shared");
        System.out.println("ok");
    }
}
