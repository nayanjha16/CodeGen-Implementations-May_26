package org.example.patterns;
public class QueueIteratorTest {
    public static void main(String[] args) {
        QueueCollection col = new QueueCollection();
        col.add("a"); col.add("b");
        if (!col.join().equals("queue:a:b")) throw new AssertionError(col.join());
        System.out.println("ok");
    }
}
