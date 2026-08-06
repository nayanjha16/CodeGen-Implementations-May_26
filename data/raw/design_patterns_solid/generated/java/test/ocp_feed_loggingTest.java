package org.example.patterns;
public class FeedOcpTest {
    public static void main(String[] args) {
        if (new FeedPriceEngine(new FeedTenPercent()).quote(100) != 90) throw new AssertionError();
        System.out.println("ok");
    }
}
