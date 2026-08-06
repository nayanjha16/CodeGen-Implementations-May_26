package org.example.patterns;
public class HttpPrototypeTest {
    public static void main(String[] args) {
        HttpPrototype a = new HttpPrototype("http", 2);
        HttpPrototype b = a.copy();
        b.setLabel("http-copy");
        if (a.describe().equals(b.describe())) throw new AssertionError();
        System.out.println("ok");
    }
}
