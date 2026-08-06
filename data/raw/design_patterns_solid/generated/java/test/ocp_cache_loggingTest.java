package org.example.patterns;
public class CacheOcpTest {
    public static void main(String[] args) {
        if (new CachePriceEngine(new CacheTenPercent()).quote(100) != 90) throw new AssertionError();
        System.out.println("ok");
    }
}
