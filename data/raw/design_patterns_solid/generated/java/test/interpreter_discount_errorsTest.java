package org.example.patterns;
public class DiscountInterpreterTest {
    public static void main(String[] args) {
        DiscountInterpreter i = new DiscountInterpreter();
        if (i.eval("2+3") != 5) throw new AssertionError();
        System.out.println("ok");
    }
}
