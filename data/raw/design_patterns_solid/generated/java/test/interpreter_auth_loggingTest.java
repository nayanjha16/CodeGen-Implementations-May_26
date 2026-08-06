package org.example.patterns;
public class AuthInterpreterTest {
    public static void main(String[] args) {
        AuthInterpreter i = new AuthInterpreter();
        if (i.eval("2+3") != 5) throw new AssertionError();
        System.out.println("ok");
    }
}
