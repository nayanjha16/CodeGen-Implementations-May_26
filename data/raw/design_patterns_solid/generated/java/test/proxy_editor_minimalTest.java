package org.example.patterns;
public class EditorProxyTest {
    public static void main(String[] args) {
        if (!new EditorProxy(true).load("1").equals("real-editor:1")) throw new AssertionError();
        if (!new EditorProxy(false).load("1").equals("denied")) throw new AssertionError();
        System.out.println("ok");
    }
}
