package org.example.patterns;
public class CacheAdapterTest {
    public static void main(String[] args) {
        CacheTarget t = new CacheAdapter(new CacheLegacyApi());
        if (!t.fetch().equals("modern-cache")) throw new AssertionError(t.fetch());
        System.out.println("ok");
    }
}
