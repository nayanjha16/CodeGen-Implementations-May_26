package org.example.patterns;
public class ConfigInterpreterTest {
    public static void main(String[] args) {
        ConfigInterpreter i = new ConfigInterpreter();
        if (i.eval("2+3") != 5) throw new AssertionError();
        System.out.println("ok");
    }
}
