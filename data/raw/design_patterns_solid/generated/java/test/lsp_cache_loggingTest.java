package org.example.patterns;
public class CacheLspTest {
    public static void main(String[] args) {
        CacheShape[] arr = new CacheShape[] { new CacheRectangle(2,3), new CacheSquare(4) };
        if (CacheLspUtil.total(arr) != 22) throw new AssertionError();
        System.out.println("ok");
    }
}
