package org.example.patterns;
public class SyncAbstractFactoryTest {
    public static void main(String[] args) {
        String out = SyncAbstractFactoryDemo.run(new SyncCloudFactory());
        if (!out.equals("cloud-btn-sync|cloud-dlg-sync")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
