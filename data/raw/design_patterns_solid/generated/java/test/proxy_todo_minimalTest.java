package org.example.patterns;
public class TodoProxyTest {
    public static void main(String[] args) {
        if (!new TodoProxy(true).load("1").equals("real-todo:1")) throw new AssertionError();
        if (!new TodoProxy(false).load("1").equals("denied")) throw new AssertionError();
        System.out.println("ok");
    }
}
