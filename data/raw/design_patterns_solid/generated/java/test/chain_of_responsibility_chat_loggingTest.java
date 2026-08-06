package org.example.patterns;
public class ChatChainTest {
    public static void main(String[] args) {
        ChatHandler h = new ChatLowHandler();
        h.link(new ChatHighHandler());
        if (!h.handle(2, "m").equals("high-chat:m")) throw new AssertionError();
        System.out.println("ok");
    }
}
