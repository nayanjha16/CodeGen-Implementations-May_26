package org.example.patterns;
public class CacheAbstractFactoryTest {
    public static void main(String[] args) {
        String out = CacheAbstractFactoryDemo.run(new CacheCloudFactory());
        if (!out.equals("cloud-btn-cache|cloud-dlg-cache")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
