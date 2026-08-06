package org.example.patterns;
public class ChatDecoratorTest {
    public static void main(String[] args) {
        ChatComponent c = new ChatUpperDecorator(new ChatCore());
        String out = c.process("ab");
        if (!out.equals("CHAT:AB")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
