package org.example.patterns;
public class ChatFactoryTest {
    public static void main(String[] args) {
        ChatFactory f = new ChatFactory();
        if (!f.create("basic").operate().equals("basic-chat")) throw new AssertionError();
        if (!f.create("premium").operate().equals("premium-chat")) throw new AssertionError();
        System.out.println("ok");
    }
}
