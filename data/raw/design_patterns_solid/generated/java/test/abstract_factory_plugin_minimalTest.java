package org.example.patterns;
public class PluginAbstractFactoryTest {
    public static void main(String[] args) {
        String out = PluginAbstractFactoryDemo.run(new PluginCloudFactory());
        if (!out.equals("cloud-btn-plugin|cloud-dlg-plugin")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
