package org.example.patterns;
public class SessionInterpreterTest {
    public static void main(String[] args) {
        SessionInterpreter i = new SessionInterpreter();
        if (i.eval("2+3") != 5) throw new AssertionError();
        System.out.println("ok");
    }
}
