package org.example.patterns;
public class MapAbstractFactoryTest {
    public static void main(String[] args) {
        String out = MapAbstractFactoryDemo.run(new MapCloudFactory());
        if (!out.equals("cloud-btn-map|cloud-dlg-map")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
