package org.example.patterns;
public class GameProxyTest {
    public static void main(String[] args) {
        if (!new GameProxy(true).load("1").equals("real-game:1")) throw new AssertionError();
        if (!new GameProxy(false).load("1").equals("denied")) throw new AssertionError();
        System.out.println("ok");
    }
}
