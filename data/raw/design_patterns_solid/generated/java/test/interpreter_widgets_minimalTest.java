package org.example.patterns;
public class WidgetsInterpreterTest {
    public static void main(String[] args) {
        WidgetsInterpreter i = new WidgetsInterpreter();
        if (i.eval("2+3") != 5) throw new AssertionError();
        System.out.println("ok");
    }
}
