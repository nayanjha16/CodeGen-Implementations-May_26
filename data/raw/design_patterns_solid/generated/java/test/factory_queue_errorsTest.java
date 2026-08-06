package org.example.patterns;
public class QueueFactoryTest {
    public static void main(String[] args) {
        QueueFactory f = new QueueFactory();
        if (!f.create("basic").operate().equals("basic-queue")) throw new AssertionError();
        if (!f.create("premium").operate().equals("premium-queue")) throw new AssertionError();
        System.out.println("ok");
    }
}
