package org.example.patterns;
public class ChatLspTest {
    public static void main(String[] args) {
        ChatShape[] arr = new ChatShape[] { new ChatRectangle(2,3), new ChatSquare(4) };
        if (ChatLspUtil.total(arr) != 22) throw new AssertionError();
        System.out.println("ok");
    }
}
