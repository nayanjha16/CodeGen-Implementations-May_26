package org.example.patterns;
public class CanvasInterpreterTest {
    public static void main(String[] args) {
        CanvasInterpreter i = new CanvasInterpreter();
        if (i.eval("2+3") != 5) throw new AssertionError();
        System.out.println("ok");
    }
}
