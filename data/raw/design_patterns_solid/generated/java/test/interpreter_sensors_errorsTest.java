package org.example.patterns;
public class SensorsInterpreterTest {
    public static void main(String[] args) {
        SensorsInterpreter i = new SensorsInterpreter();
        if (i.eval("2+3") != 5) throw new AssertionError();
        System.out.println("ok");
    }
}
