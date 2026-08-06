package org.example.patterns;
public class NotesProxyTest {
    public static void main(String[] args) {
        if (!new NotesProxy(true).load("1").equals("real-notes:1")) throw new AssertionError();
        if (!new NotesProxy(false).load("1").equals("denied")) throw new AssertionError();
        System.out.println("ok");
    }
}
