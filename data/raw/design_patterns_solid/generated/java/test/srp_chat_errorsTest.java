package org.example.patterns;
public class ChatSrpTest {
    public static void main(String[] args) {
        ChatRecord r = new ChatRecord("a", 3);
        if (!new ChatFormatter().format(r).equals("a=3")) throw new AssertionError();
        System.out.println("ok");
    }
}
