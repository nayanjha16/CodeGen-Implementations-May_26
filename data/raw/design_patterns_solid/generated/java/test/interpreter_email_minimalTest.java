package org.example.patterns;
public class EmailInterpreterTest {
    public static void main(String[] args) {
        EmailInterpreter i = new EmailInterpreter();
        if (i.eval("2+3") != 5) throw new AssertionError();
        System.out.println("ok");
    }
}
