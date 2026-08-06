package org.example.patterns;
public class QueueIspTest {
    public static void main(String[] args) {
        QueueStore st = new QueueStore();
        st.write("x");
        if (!QueueIspClient.mirror(st).equals("queue:x")) throw new AssertionError();
        System.out.println("ok");
    }
}
