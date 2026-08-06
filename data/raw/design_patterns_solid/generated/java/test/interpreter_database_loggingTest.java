package org.example.patterns;
public class DatabaseInterpreterTest {
    public static void main(String[] args) {
        DatabaseInterpreter i = new DatabaseInterpreter();
        if (i.eval("2+3") != 5) throw new AssertionError();
        System.out.println("ok");
    }
}
