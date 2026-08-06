package org.example.patterns;
public class ConfigAdapterTest {
    public static void main(String[] args) {
        ConfigTarget t = new ConfigAdapter(new ConfigLegacyApi());
        if (!t.fetch().equals("modern-config")) throw new AssertionError(t.fetch());
        System.out.println("ok");
    }
}
