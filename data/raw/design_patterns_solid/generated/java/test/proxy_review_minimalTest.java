package org.example.patterns;
public class ReviewProxyTest {
    public static void main(String[] args) {
        if (!new ReviewProxy(true).load("1").equals("real-review:1")) throw new AssertionError();
        if (!new ReviewProxy(false).load("1").equals("denied")) throw new AssertionError();
        System.out.println("ok");
    }
}
