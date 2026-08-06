package org.example.patterns;
public class CacheFactoryTest {
    public static void main(String[] args) {
        CacheFactory f = new CacheFactory();
        if (!f.create("basic").operate().equals("basic-cache")) throw new AssertionError();
        if (!f.create("premium").operate().equals("premium-cache")) throw new AssertionError();
        System.out.println("ok");
    }
}
