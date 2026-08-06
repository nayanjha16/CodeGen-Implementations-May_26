package org.example.patterns;
public class SearchProxyTest {
    public static void main(String[] args) {
        if (!new SearchProxy(true).load("1").equals("real-search:1")) throw new AssertionError();
        if (!new SearchProxy(false).load("1").equals("denied")) throw new AssertionError();
        System.out.println("ok");
    }
}
