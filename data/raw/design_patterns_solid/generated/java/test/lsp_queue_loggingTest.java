package org.example.patterns;
public class QueueLspTest {
    public static void main(String[] args) {
        QueueShape[] arr = new QueueShape[] { new QueueRectangle(2,3), new QueueSquare(4) };
        if (QueueLspUtil.total(arr) != 22) throw new AssertionError();
        System.out.println("ok");
    }
}
