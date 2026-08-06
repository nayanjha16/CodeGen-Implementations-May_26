package org.example.patterns;
public class HttpAbstractFactoryTest {
    public static void main(String[] args) {
        String out = HttpAbstractFactoryDemo.run(new HttpCloudFactory());
        if (!out.equals("cloud-btn-http|cloud-dlg-http")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
