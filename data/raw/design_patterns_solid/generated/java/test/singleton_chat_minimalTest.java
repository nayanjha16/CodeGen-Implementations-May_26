package org.example.patterns;
public class ChatSingletonTest {
    public static void main(String[] args) {
        ChatSingleton a = ChatSingleton.getInstance();
        ChatSingleton b = ChatSingleton.getInstance();
        a.setValue("chat-one");
        if (a != b) throw new AssertionError("not singleton");
        if (!b.getValue().equals("chat-one")) throw new AssertionError("state not shared");
        System.out.println("ok");
    }
}
