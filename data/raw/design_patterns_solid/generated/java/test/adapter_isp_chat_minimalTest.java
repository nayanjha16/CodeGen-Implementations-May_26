package org.example.patterns;
public class ChatAdapterTest {
    public static void main(String[] args) {
        ChatTarget t = new ChatAdapter(new ChatLegacyApi());
        if (!t.fetch().equals("modern-chat")) throw new AssertionError(t.fetch());
        System.out.println("ok");
    }
}
