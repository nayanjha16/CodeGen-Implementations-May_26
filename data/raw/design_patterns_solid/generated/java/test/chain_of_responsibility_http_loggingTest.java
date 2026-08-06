package org.example.patterns;
public class HttpChainTest {
    public static void main(String[] args) {
        HttpHandler h = new HttpLowHandler();
        h.link(new HttpHighHandler());
        if (!h.handle(2, "m").equals("high-http:m")) throw new AssertionError();
        System.out.println("ok");
    }
}
