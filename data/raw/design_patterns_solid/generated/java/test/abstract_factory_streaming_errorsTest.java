package org.example.patterns;
public class StreamingAbstractFactoryTest {
    public static void main(String[] args) {
        String out = StreamingAbstractFactoryDemo.run(new StreamingCloudFactory());
        if (!out.equals("cloud-btn-streaming|cloud-dlg-streaming")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
