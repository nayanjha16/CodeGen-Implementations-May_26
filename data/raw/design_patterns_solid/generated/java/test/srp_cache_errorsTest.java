package org.example.patterns;
public class CacheSrpTest {
    public static void main(String[] args) {
        CacheRecord r = new CacheRecord("a", 3);
        if (!new CacheFormatter().format(r).equals("a=3")) throw new AssertionError();
        System.out.println("ok");
    }
}
