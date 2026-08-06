package org.example.patterns;
public class CanvasAdapterTest {
    public static void main(String[] args) {
        CanvasTarget t = new CanvasAdapter(new CanvasLegacyApi());
        if (!t.fetch().equals("modern-canvas")) throw new AssertionError(t.fetch());
        System.out.println("ok");
    }
}
