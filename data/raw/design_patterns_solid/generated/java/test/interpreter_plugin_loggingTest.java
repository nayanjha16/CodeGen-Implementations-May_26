package org.example.patterns;
public class PluginInterpreterTest {
    public static void main(String[] args) {
        PluginInterpreter i = new PluginInterpreter();
        if (i.eval("2+3") != 5) throw new AssertionError();
        System.out.println("ok");
    }
}
