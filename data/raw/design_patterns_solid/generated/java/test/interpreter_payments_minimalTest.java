package org.example.patterns;
public class PaymentsInterpreterTest {
    public static void main(String[] args) {
        PaymentsInterpreter i = new PaymentsInterpreter();
        if (i.eval("2+3") != 5) throw new AssertionError();
        System.out.println("ok");
    }
}
