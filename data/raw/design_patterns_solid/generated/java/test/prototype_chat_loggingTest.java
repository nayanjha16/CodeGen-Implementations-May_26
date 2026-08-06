package org.example.patterns;
public class ChatPrototypeTest {
    public static void main(String[] args) {
        ChatPrototype a = new ChatPrototype("chat", 2);
        ChatPrototype b = a.copy();
        b.setLabel("chat-copy");
        if (a.describe().equals(b.describe())) throw new AssertionError();
        System.out.println("ok");
    }
}
