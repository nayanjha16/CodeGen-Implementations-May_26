package org.example.patterns;
public class QueueStateTest {
    public static void main(String[] args) {
        QueueContext ctx = new QueueContext();
        if (!ctx.request().equals("was-off-queue")) throw new AssertionError();
        if (!ctx.request().equals("was-on-queue")) throw new AssertionError();
        System.out.println("ok");
    }
}
