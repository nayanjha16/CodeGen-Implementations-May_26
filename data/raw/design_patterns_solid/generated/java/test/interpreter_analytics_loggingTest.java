package org.example.patterns;
public class AnalyticsInterpreterTest {
    public static void main(String[] args) {
        AnalyticsInterpreter i = new AnalyticsInterpreter();
        if (i.eval("2+3") != 5) throw new AssertionError();
        System.out.println("ok");
    }
}
