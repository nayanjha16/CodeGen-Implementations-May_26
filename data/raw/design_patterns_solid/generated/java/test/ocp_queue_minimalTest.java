package org.example.patterns;
public class QueueOcpTest {
    public static void main(String[] args) {
        if (new QueuePriceEngine(new QueueTenPercent()).quote(100) != 90) throw new AssertionError();
        System.out.println("ok");
    }
}
