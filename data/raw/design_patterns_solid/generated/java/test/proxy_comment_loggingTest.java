package org.example.patterns;
public class CommentProxyTest {
    public static void main(String[] args) {
        if (!new CommentProxy(true).load("1").equals("real-comment:1")) throw new AssertionError();
        if (!new CommentProxy(false).load("1").equals("denied")) throw new AssertionError();
        System.out.println("ok");
    }
}
