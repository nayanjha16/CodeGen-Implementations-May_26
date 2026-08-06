package org.example.patterns;
public class BillingInterpreterTest {
    public static void main(String[] args) {
        BillingInterpreter i = new BillingInterpreter();
        if (i.eval("2+3") != 5) throw new AssertionError();
        System.out.println("ok");
    }
}
