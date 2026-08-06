package org.example.patterns;
public class ChatFacadeTest {
    public static void main(String[] args) {
        ChatFacade f = new ChatFacade();
        if (!f.submit("x").equals("wrote-chat:x")) throw new AssertionError();
        System.out.println("ok");
    }
}
