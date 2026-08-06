package org.example.patterns;
public class TodoInterpreterTest {
    public static void main(String[] args) {
        TodoInterpreter i = new TodoInterpreter();
        if (i.eval("2+3") != 5) throw new AssertionError();
        System.out.println("ok");
    }
}
