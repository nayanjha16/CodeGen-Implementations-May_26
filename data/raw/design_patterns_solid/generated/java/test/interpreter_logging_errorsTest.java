package org.example.patterns;
public class LoggingInterpreterTest {
    public static void main(String[] args) {
        LoggingInterpreter i = new LoggingInterpreter();
        if (i.eval("2+3") != 5) throw new AssertionError();
        System.out.println("ok");
    }
}
