package org.example.patterns;
public class HttpSingletonTest {
    public static void main(String[] args) {
        HttpSingleton a = HttpSingleton.getInstance();
        HttpSingleton b = HttpSingleton.getInstance();
        a.setValue("http-one");
        if (a != b) throw new AssertionError("not singleton");
        if (!b.getValue().equals("http-one")) throw new AssertionError("state not shared");
        System.out.println("ok");
    }
}
