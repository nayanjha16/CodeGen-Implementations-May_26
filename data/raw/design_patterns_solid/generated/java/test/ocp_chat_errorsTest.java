package org.example.patterns;
public class ChatOcpTest {
    public static void main(String[] args) {
        if (new ChatPriceEngine(new ChatTenPercent()).quote(100) != 90) throw new AssertionError();
        System.out.println("ok");
    }
}
