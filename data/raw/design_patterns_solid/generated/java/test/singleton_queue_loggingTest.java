package org.example.patterns;
public class QueueSingletonTest {
    public static void main(String[] args) {
        QueueSingleton a = QueueSingleton.getInstance();
        QueueSingleton b = QueueSingleton.getInstance();
        a.setValue("queue-one");
        if (a != b) throw new AssertionError("not singleton");
        if (!b.getValue().equals("queue-one")) throw new AssertionError("state not shared");
        System.out.println("ok");
    }
}
