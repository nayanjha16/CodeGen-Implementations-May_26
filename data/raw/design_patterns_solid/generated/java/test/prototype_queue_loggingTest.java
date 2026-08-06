package org.example.patterns;
public class QueuePrototypeTest {
    public static void main(String[] args) {
        QueuePrototype a = new QueuePrototype("queue", 2);
        QueuePrototype b = a.copy();
        b.setLabel("queue-copy");
        if (a.describe().equals(b.describe())) throw new AssertionError();
        System.out.println("ok");
    }
}
