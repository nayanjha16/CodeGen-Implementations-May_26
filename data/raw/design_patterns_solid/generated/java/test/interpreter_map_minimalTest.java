package org.example.patterns;
public class MapInterpreterTest {
    public static void main(String[] args) {
        MapInterpreter i = new MapInterpreter();
        if (i.eval("2+3") != 5) throw new AssertionError();
        System.out.println("ok");
    }
}
