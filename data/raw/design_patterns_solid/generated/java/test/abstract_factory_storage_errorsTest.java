package org.example.patterns;
public class StorageAbstractFactoryTest {
    public static void main(String[] args) {
        String out = StorageAbstractFactoryDemo.run(new StorageCloudFactory());
        if (!out.equals("cloud-btn-storage|cloud-dlg-storage")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
