package org.example.patterns;
public class QueueAdapterTest {
    public static void main(String[] args) {
        QueueTarget t = new QueueAdapter(new QueueLegacyApi());
        if (!t.fetch().equals("modern-queue")) throw new AssertionError(t.fetch());
        System.out.println("ok");
    }
}
