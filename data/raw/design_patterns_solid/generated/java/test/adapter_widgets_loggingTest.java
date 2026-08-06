package org.example.patterns;
public class WidgetsAdapterTest {
    public static void main(String[] args) {
        WidgetsTarget t = new WidgetsAdapter(new WidgetsLegacyApi());
        if (!t.fetch().equals("modern-widgets")) throw new AssertionError(t.fetch());
        System.out.println("ok");
    }
}
