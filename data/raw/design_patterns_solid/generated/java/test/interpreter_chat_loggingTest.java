package org.example.patterns;
public class ChatInterpreterTest {
    public static void main(String[] args) {
        ChatInterpreter i = new ChatInterpreter();
        if (i.eval("2+3") != 5) throw new AssertionError();
        System.out.println("ok");
    }
}
