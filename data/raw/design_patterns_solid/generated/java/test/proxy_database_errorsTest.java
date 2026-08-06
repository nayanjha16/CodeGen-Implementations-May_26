package org.example.patterns;
public class DatabaseProxyTest {
    public static void main(String[] args) {
        if (!new DatabaseProxy(true).load("1").equals("real-database:1")) throw new AssertionError();
        if (!new DatabaseProxy(false).load("1").equals("denied")) throw new AssertionError();
        System.out.println("ok");
    }
}
