package org.example.patterns;
public class FeedDipTest {
    public static void main(String[] args) {
        String out = new FeedAppService(new FeedHttpGateway()).publish("p");
        if (!out.equals("http-feed:p")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
