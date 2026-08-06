package org.example.patterns;
public class SyncOcpTest {
    public static void main(String[] args) {
        if (new SyncPriceEngine(new SyncTenPercent()).quote(100) != 90) throw new AssertionError();
        System.out.println("ok");
    }
}
