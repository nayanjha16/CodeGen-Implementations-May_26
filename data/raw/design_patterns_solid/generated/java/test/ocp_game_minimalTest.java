package org.example.patterns;
public class GameOcpTest {
    public static void main(String[] args) {
        if (new GamePriceEngine(new GameTenPercent()).quote(100) != 90) throw new AssertionError();
        System.out.println("ok");
    }
}
