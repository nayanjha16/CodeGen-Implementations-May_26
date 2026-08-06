package org.example.patterns;
public class MetricsInterpreterTest {
    public static void main(String[] args) {
        MetricsInterpreter i = new MetricsInterpreter();
        if (i.eval("2+3") != 5) throw new AssertionError();
        System.out.println("ok");
    }
}
