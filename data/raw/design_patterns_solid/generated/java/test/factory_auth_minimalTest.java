package org.example.patterns;
public class AuthFactoryTest {
    public static void main(String[] args) {
        AuthFactory f = new AuthFactory();
        if (!f.create("basic").operate().equals("basic-auth")) throw new AssertionError();
        if (!f.create("premium").operate().equals("premium-auth")) throw new AssertionError();
        System.out.println("ok");
    }
}
