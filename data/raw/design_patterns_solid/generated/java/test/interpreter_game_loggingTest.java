package org.example.patterns;
public class GameInterpreterTest {
    public static void main(String[] args) {
        GameInterpreter i = new GameInterpreter();
        if (i.eval("2+3") != 5) throw new AssertionError();
        System.out.println("ok");
    }
}
