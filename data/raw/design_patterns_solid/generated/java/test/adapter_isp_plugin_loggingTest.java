package org.example.patterns;
public class PluginAdapterTest {
    public static void main(String[] args) {
        PluginTarget t = new PluginAdapter(new PluginLegacyApi());
        if (!t.fetch().equals("modern-plugin")) throw new AssertionError(t.fetch());
        System.out.println("ok");
    }
}
